
class Helpers:
    def to_text(content) -> str:
        """Convert Gradio message content to a plain string for the Agents SDK."""
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    parts.append(block.get("text") or block.get("content") or "")
                else:
                    parts.append(str(block))
            return "\n".join(p for p in parts if p)
        if isinstance(content, dict):
            return content.get("text") or content.get("content") or str(content)
        return str(content)