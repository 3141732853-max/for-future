# Installation and adapters / 安装与适配

`skills/chainwright/SKILL.md` is the canonical behavior specification. The Chinese companion explains the same workflow. Generated prompt adapters carry a hash of the source.

## Native skill hosts

Copy the entire `chainwright` folder, preserving scripts, references, assets and agents. The path must be one level below the skill root: `<root>/chainwright/SKILL.md`.

| Host | Project | Personal | Reference |
| --- | --- | --- | --- |
| DeepSeek Harness | `.dsh/skills/chainwright` | `~/.dsh/skills/chainwright` | [Official filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md) |
| Codex | `.agents/skills/chainwright` | `~/.agents/skills/chainwright` | [OpenAI documentation](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `.claude/skills/chainwright` | `~/.claude/skills/chainwright` | [Claude documentation](https://code.claude.com/docs/en/skills) |

DSH requires its skill registry/filesystem provider. A custom DSH_HOME changes the personal root; disabling default roots requires explicit configuration. Only direct skill bundles are discovered, so avoid nesting `chainwright/chainwright/SKILL.md`. Install in the runtime environment: Windows, WSL, container or remote host.

Confirm the host lists and loads Chainwright; ask it to explain the working modes before giving it a small task. Script execution additionally needs Python 3.10+ and a permitted execution tool. Discovery is not proof of execution or quality.

复制完整目录，并确认宿主确实能列出与加载技能。DSH 的个人目录可能被 DSH_HOME 改写；在 WSL、容器或远程运行时，应安装在对应环境。不要多套一层目录。Python 与执行权限是运行检查脚本的额外条件。

## Prompt-only hosts

For ChatGPT without a native skill surface or another instruction-only host, use `adapters/minimal.txt` as a small instruction excerpt. Supply `adapters/system-prompt.md` for the full workflow. A prompt does not register tools or grant file access; unavailable checks remain not run.

```sh
python skills/chainwright/scripts/export_adapters.py --out adapters
python skills/chainwright/scripts/export_adapters.py --out adapters --check
```

These commands regenerate files; they do not change host settings. `adapters/manifest.json` records the source hash.

纯提示词宿主使用最小常驻片段和按需完整协议。适配文件自动生成，不单独维护第二套规则；没有工具时用文字检查记录，并说明哪些检查未运行。

## Compatibility status

Format and script checks are automated. Native loading paths are documented by the respective vendors. Live loading/execution across all hosts has not been certified; account, version and tool policies can change availability.
