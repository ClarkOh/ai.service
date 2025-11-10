# ai_chat_simple_test.py
# simple test for gemini chat api

import google.generativeai as genai
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timezone
import struct

class GeminiChat:
    def __init__(self, api_key=None, model="gemini-2.5-flash"):

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._load_api_key_from_file()

        if not self.api_key:
            raise ValueError("API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.default_reply_language = "한국어"
        self._create_chat_session()

        # Safety configuration (restrictions relaxed)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    
    def _load_api_key_from_file(self):
        key_file = Path("gemini.api.key.txt")
        if key_file.exists():
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        print(f"[OK] API key loaded from key file")
                        return api_key
            except Exception as e:
                print(f"[WARNING] Error reading gemini.api.key.txt: {e}")
        return None

    def chat(self, prompt: str) -> str:
        try:
            response = self.chat_session.send_message(
                prompt,
                safety_settings=self.safety_settings
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def _create_chat_session(self) -> None:
        """Create a new chat session with default language priming."""
        self.chat_session = self.model.start_chat(history=[])
        try:
            self.chat_session.send_message(
                f"당신은 친근한 AI 비서입니다. 앞으로 모든 응답은 {self.default_reply_language}로 작성하고, "
                "명확하고 간결하게 답변하세요."
            )
        except Exception as exc:
            print(f"[WARNING] Failed to prime chat session: {exc}")

    def reset_chat(self) -> None:
        """Reset the ongoing chat session."""
        self._create_chat_session()

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the accumulated conversation history."""
        return self.chat_session.history

    def analyze_pcap(self, file_path: str, analysis_goal: str = "", max_packets: int = 50) -> str:
        """
        Parse a PCAP file locally and request an analysis from Gemini.

        Args:
            file_path (str): Path to the PCAP capture.
            analysis_goal (str): High-level question or focus area from the user.
            max_packets (int): Maximum number of packets to include in the sample section.

        Returns:
            str: Analysis result or an error message.
        """
        try:
            with open(file_path, "rb") as handle:
                header_peek = handle.read(4)
                if len(header_peek) < 4:
                    return "Error: File is too small to be a valid capture."

                magic_number = struct.unpack("<I", header_peek)[0]

                if magic_number in (0xA1B2C3D4, 0xD4C3B2A1, 0xA1B23C4D, 0x4D3CB2A1):
                    handle.seek(0)
                    summary = self._parse_pcap_legacy(handle, max_packets)
                elif magic_number == 0x0A0D0D0A:
                    handle.seek(0)
                    summary = self._parse_pcapng(handle, max_packets)
                else:
                    return "Error: Unsupported capture format or magic number."

                if isinstance(summary, str) and summary.startswith("Error:"):
                    return summary

                metadata_lines, ether_section, sample_section = summary

                goal_text = analysis_goal.strip() or "전반적인 트래픽 특성, 이상 징후, 보안 이슈를 중심으로 분석해주세요."

                analysis_prompt = (
                    "You are a professional network analyst.\n"
                    "Use the following packet capture summary to provide insights about the traffic:\n\n"
                    "=== Capture Metadata ===\n"
                    f"{chr(10).join(metadata_lines)}\n\n"
                    "=== Top EtherTypes ===\n"
                    f"{ether_section}\n\n"
                    "=== Sample Packets ===\n"
                    f"{sample_section}\n\n"
                    f"User analysis request (Korean): {goal_text}\n\n"
                    "Discuss the likely traffic types, noteworthy observations, and any potential security concerns. "
                    "If additional data would help clarify the situation, mention it explicitly. "
                    "Respond in Korean."
                )

                response = self.model.generate_content(
                    analysis_prompt,
                    safety_settings=self.safety_settings
                )
                return response.text.strip()

        except FileNotFoundError:
            return f"Error: File '{file_path}' not found."
        except PermissionError:
            return f"Error: Permission denied when reading '{file_path}'."
        except Exception as exc:
            return f"Error while processing PCAP: {exc}"

    def _parse_pcap_legacy(self, handle, max_packets):
        global_header = handle.read(24)
        if len(global_header) < 24:
            return "Error: File is too small to be a valid PCAP capture."

        magic_number = struct.unpack("<I", global_header[:4])[0]
        if magic_number == 0xA1B2C3D4:
            endian = "<"
            ts_resolution = "micro"
        elif magic_number == 0xD4C3B2A1:
            endian = ">"
            ts_resolution = "micro"
        elif magic_number == 0xA1B23C4D:
            endian = "<"
            ts_resolution = "nano"
        elif magic_number == 0x4D3CB2A1:
            endian = ">"
            ts_resolution = "nano"
        else:
            return "Error: Unsupported PCAP magic number."

        header_fmt = endian + "HHIIII"
        (_ver_major, _ver_minor, _thiszone, _sigfigs, snaplen, network) = struct.unpack(
            header_fmt, global_header[4:]
        )

        packet_header_fmt = endian + "IIII"
        total_packets = 0
        total_bytes = 0
        earliest_ts = None
        latest_ts = None
        ether_types = Counter()
        sample_entries = []

        while True:
            packet_header = handle.read(16)
            if len(packet_header) < 16:
                break

            ts_sec, ts_subsec, captured_len, original_len = struct.unpack(
                packet_header_fmt, packet_header
            )
            packet_data = handle.read(captured_len)
            if len(packet_data) < captured_len:
                break

            total_packets += 1
            total_bytes += captured_len

            ts_float = ts_sec + (ts_subsec / (1_000_000 if ts_resolution == "micro" else 1_000_000_000))
            if earliest_ts is None or ts_float < earliest_ts:
                earliest_ts = ts_float
            if latest_ts is None or ts_float > latest_ts:
                latest_ts = ts_float

            if captured_len >= 14:
                ether_type = struct.unpack("!H", packet_data[12:14])[0]
                ether_types[ether_type] += 1
            else:
                ether_types["<truncated>"] += 1

                if len(sample_entries) < max_packets:
                    timestamp = datetime.fromtimestamp(ts_float, timezone.utc).isoformat()
                preview = packet_data[:32].hex()
                sample_entries.append(
                        f"- ts={timestamp}, captured={captured_len}, original={original_len}, preview={preview}"
                )

        if total_packets == 0:
            return "Error: No packets found in the capture."

        duration = 0.0
        if earliest_ts is not None and latest_ts is not None:
            duration = max(0.0, latest_ts - earliest_ts)

        metadata_lines = [
            f"File path: {getattr(handle, 'name', '<memory>')}",
            f"Capture type: PCAP (legacy)",
            f"Link-layer type (network): {network}",
            f"Snapshot length: {snaplen}",
            f"Total packets: {total_packets}",
            f"Total captured bytes: {total_bytes}",
            f"Capture duration (approx): {duration:.6f} seconds",
        ]
        if earliest_ts is not None:
            metadata_lines.append(
                f"Earliest timestamp (UTC): {datetime.fromtimestamp(earliest_ts, timezone.utc).isoformat()}"
            )
        if latest_ts is not None:
            metadata_lines.append(
                f"Latest timestamp (UTC): {datetime.fromtimestamp(latest_ts, timezone.utc).isoformat()}"
            )

        human_ether = []
        for eid, count in ether_types.most_common(5):
            label = self._describe_ethertype(eid)
            human_ether.append(f"- {label}: {count} packet(s)")

        ether_section = "\n".join(human_ether) if human_ether else "No EtherType information."
        sample_section = "\n".join(sample_entries) if sample_entries else "No packet samples available."
        return metadata_lines, ether_section, sample_section

    def _parse_pcapng(self, handle, max_packets):
        data = handle.read()
        offset = 0
        total_len = len(data)
        if total_len < 12:
            return "Error: File is too small to be a valid PCAPNG capture."

        total_packets = 0
        total_bytes = 0
        earliest_ts = None
        latest_ts = None
        ether_types = Counter()
        sample_entries = []
        snaplen_map = {}
        linktype_map = {}

        while offset + 8 <= total_len:
            block_type, block_total_length = struct.unpack_from("<II", data, offset)
            if block_total_length < 12 or offset + block_total_length > total_len:
                return "Error: Malformed PCAPNG block encountered."

            body_offset = offset + 8
            body_length = block_total_length - 12
            body_data = data[body_offset: body_offset + body_length]
            trailing_length = struct.unpack_from("<I", data, offset + block_total_length - 4)[0]
            if trailing_length != block_total_length:
                return "Error: PCAPNG block length mismatch."

            if block_type == 0x0A0D0D0A:  # Section Header Block
                if body_length < 12:
                    return "Error: PCAPNG Section Header Block too short."
                byte_order_magic = struct.unpack_from("<I", body_data, 0)[0]
                if byte_order_magic == 0x1A2B3C4D:
                    endian = "<"
                elif byte_order_magic == 0x4D3C2B1A:
                    endian = ">"
                else:
                    return "Error: Unsupported PCAPNG byte-order magic."
                # Update struct formats based on endian
                idb_fmt = endian + "H H I"
                epb_fmt = endian + "I I I I I"
            elif block_type == 0x00000001:  # Interface Description Block
                if len(body_data) < 8:
                    return "Error: PCAPNG Interface Description Block too short."
                linktype, _reserved, snaplen = struct.unpack_from(idb_fmt, body_data, 0)
                snaplen_map[len(snaplen_map)] = snaplen
                linktype_map[len(linktype_map)] = linktype
            elif block_type == 0x00000006:  # Enhanced Packet Block
                if len(body_data) < 20:
                    offset += block_total_length
                    continue
                interface_id, ts_high, ts_low, captured_len, packet_len = struct.unpack_from(epb_fmt, body_data, 0)
                packet_start = 20
                packet_end = packet_start + captured_len
                if packet_end > len(body_data):
                    offset += block_total_length
                    continue
                packet_data = body_data[packet_start:packet_end]

                ts_resolution = 1_000_000  # default microsecond unless resolved via options
                ts_combined = (ts_high << 32) | ts_low
                ts_float = ts_combined / ts_resolution

                total_packets += 1
                total_bytes += captured_len

                if earliest_ts is None or ts_float < earliest_ts:
                    earliest_ts = ts_float
                if latest_ts is None or ts_float > latest_ts:
                    latest_ts = ts_float

                if captured_len >= 14:
                    ether_type = struct.unpack("!H", packet_data[12:14])[0]
                    ether_types[ether_type] += 1
                else:
                    ether_types["<truncated>"] += 1

                if len(sample_entries) < max_packets:
                    timestamp = datetime.fromtimestamp(ts_float, timezone.utc).isoformat()
                    preview = packet_data[:32].hex()
                    sample_entries.append(
                        f"- ts={timestamp}, captured={captured_len}, original={packet_len}, preview={preview}"
                    )
            # Other block types are ignored for now.

            offset += block_total_length

        if total_packets == 0:
            return "Error: No packets found in the capture."

        duration = 0.0
        if earliest_ts is not None and latest_ts is not None:
            duration = max(0.0, latest_ts - earliest_ts)

        primary_linktype = linktype_map.get(0, "unknown")
        primary_snaplen = snaplen_map.get(0, "unknown")

        metadata_lines = [
            f"File path: {getattr(handle, 'name', '<memory>')}",
            f"Capture type: PCAPNG",
            f"Primary link-layer type: {primary_linktype}",
            f"Primary snapshot length: {primary_snaplen}",
            f"Total packets: {total_packets}",
            f"Total captured bytes: {total_bytes}",
            f"Capture duration (approx): {duration:.6f} seconds",
        ]
        if earliest_ts is not None:
            metadata_lines.append(
                f"Earliest timestamp (UTC): {datetime.fromtimestamp(earliest_ts, timezone.utc).isoformat()}"
            )
        if latest_ts is not None:
            metadata_lines.append(
                f"Latest timestamp (UTC): {datetime.fromtimestamp(latest_ts, timezone.utc).isoformat()}"
            )

        human_ether = []
        for eid, count in ether_types.most_common(5):
            label = self._describe_ethertype(eid)
            human_ether.append(f"- {label}: {count} packet(s)")

        ether_section = "\n".join(human_ether) if human_ether else "No EtherType information."
        sample_section = "\n".join(sample_entries) if sample_entries else "No packet samples available."
        return metadata_lines, ether_section, sample_section

    @staticmethod
    def _describe_ethertype(ether_type) -> str:
        """Return a human-friendly label for a given EtherType value."""
        if isinstance(ether_type, str):
            return ether_type

        descriptions = {
            0x0800: "0x0800 (IPv4)",
            0x0806: "0x0806 (ARP)",
            0x0842: "0x0842 (Wake-on-LAN)",
            0x22F3: "0x22F3 (IETF TRILL)",
            0x6003: "0x6003 (DECnet)",
            0x8035: "0x8035 (RARP)",
            0x809B: "0x809B (Appletalk)",
            0x80F3: "0x80F3 (AARP)",
            0x8100: "0x8100 (VLAN Tagged)",
            0x86DD: "0x86DD (IPv6)",
            0x8808: "0x8808 (Ethernet Flow Control)",
            0x8809: "0x8809 (Ethernet Slow Protocols)",
            0x8847: "0x8847 (MPLS Unicast)",
            0x8848: "0x8848 (MPLS Multicast)",
            0x8863: "0x8863 (PPPoE Discovery)",
            0x8864: "0x8864 (PPPoE Session)",
            0x88A8: "0x88A8 (Q-in-Q)",
            0x88CC: "0x88CC (LLDP)",
            0x88E5: "0x88E5 (MACsec)",
            0x88F7: "0x88F7 (PTP)",
            0x8906: "0x8906 (Fibre Channel over Ethernet)",
            0x8914: "0x8914 (FCoE Initialization)",
            0x9100: "0x9100 (VLAN Tagged - double tagged)",
        }
        return descriptions.get(ether_type, f"0x{ether_type:04X}")

    def summarize(self, text):
        try:
            response = self.model.generate_content(
                text,
                safety_settings=self.safety_settings
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

def chat_main():
    chat = GeminiChat()
    print("=" * 60)
    print("Gemini Chat")
    print("Commands: 'history', 'history_reset', 'pcap <path>', 'exit'")
    print("=" * 60)
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break
        if prompt.lower() == "history_reset":
            chat.reset_chat()
            print("Gemini: Conversation summary has been reset.")
            continue
        if prompt.lower() == "history":
            history = chat.get_history()
            if not history:
                print("Gemini: No history yet.")
            else:
                print("-" * 60)
                print("Conversation History:")
                for entry in history:
                    role = entry.get("role", "unknown").capitalize()
                    parts = entry.get("parts", [])
                    content = " ".join(part.get("text", "") for part in parts)
                    print(f"{role}: {content}")
                print("-" * 60)
            continue
        if prompt.lower().startswith("pcap "):
            path = prompt[5:].strip()
            if not path:
                print("Gemini: Please provide a file path, e.g. 'pcap capture.pcap'.")
                continue
            analysis_goal = input("Gemini: 어떤 분석을 원하시나요? (예: 보안 위협 탐지, 트래픽 요약 등) ")
            result = chat.analyze_pcap(path, analysis_goal)
            print(f"Gemini: {result}")
            continue
        response = chat.chat(prompt)
        print(f"Gemini: {response}")

if __name__ == "__main__":
    chat_main()