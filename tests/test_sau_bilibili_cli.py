import sau_commands.arguments
import sau_commands.bilibili
import asyncio
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import sau_cli


class BilibiliCliTests(unittest.TestCase):
    def test_build_parser_accepts_bilibili_login(self):
        parser = sau_cli.build_parser()
        args = parser.parse_args(["bilibili", "login", "--account", "creator"])
        self.assertEqual(args.platform, "bilibili")
        self.assertEqual(args.action, "login")

    def test_build_parser_requires_tid_for_upload_video(self):
        parser = sau_cli.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "bilibili",
                    "upload-video",
                    "--account",
                    "creator",
                    "--file",
                    "demo.mp4",
                    "--title",
                    "hello",
                    "--desc",
                    "hello",
                ]
            )

    def test_dispatch_bilibili_check_prints_valid(self):
        args = Namespace(platform="bilibili", action="check", account="creator")
        with patch("sau_commands.bilibili.check_bilibili_account", new=AsyncMock(return_value=True)):
            code = asyncio.run(sau_cli.dispatch(args))
        self.assertEqual(code, 0)

    def test_login_bilibili_account_returns_friendly_message_without_terminal(self):
        with patch("sau_commands.bilibili.has_interactive_terminal", return_value=False):
            result = asyncio.run(sau_commands.bilibili.login_bilibili_account("creator"))
        self.assertFalse(result["success"])
        self.assertIn("local interactive terminal", result["message"].lower())
        self.assertIn("qrcode.png", result["message"].lower())

    def test_upload_bilibili_video_converts_escaped_newlines_and_only_self(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            account_file = Path(temp_dir) / "account.json"
            account_file.write_text("{}", encoding="utf-8")
            request = sau_commands.bilibili.BilibiliVideoUploadRequest("creator", Path("demo.mp4"), "hello", "line1\\nline2\\r\\nline3", 201, [], 0, only_self=True)
            with patch("sau_commands.bilibili.resolve_account_file", return_value=account_file), patch("sau_commands.bilibili.run_biliup_command", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")) as run_biliup:
                asyncio.run(sau_commands.bilibili.upload_bilibili_video(request))
        arguments = run_biliup.call_args.args[0]
        self.assertEqual(arguments[arguments.index("--desc") + 1], "line1\nline2\nline3")
        self.assertEqual(arguments[arguments.index("--is-only-self") + 1], "1")

    def test_parser_accepts_cover_alias_for_bilibili(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as video:
            args = sau_cli.build_parser().parse_args(["bilibili", "upload-video", "--account", "a", "--file", video.name, "--title", "t", "--desc", "d", "--tid", "201", "--cover", video.name, "--only-self"])
        self.assertEqual(str(args.thumbnail), video.name)
        self.assertTrue(args.only_self)

    def test_upload_bilibili_video_passes_thumbnail_to_biliup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            account_file = Path(temp_dir) / "account.json"
            account_file.write_text("{}", encoding="utf-8")
            request = sau_commands.bilibili.BilibiliVideoUploadRequest("creator", Path("demo.mp4"), "hello", "hello", 249, ["test"], 0, Path("cover.png"))
            with patch("sau_commands.bilibili.resolve_account_file", return_value=account_file), patch("sau_commands.bilibili.run_biliup_command", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")) as run_biliup:
                asyncio.run(sau_commands.bilibili.upload_bilibili_video(request))
        self.assertIn("--cover", run_biliup.call_args.args[0])
        self.assertIn("cover.png", run_biliup.call_args.args[0])
