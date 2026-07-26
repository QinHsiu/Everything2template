# Pro README

Thank you for purchasing Everything2template Pro.

## Install

1. Keep Hobby core installed (`pip install -e .` from the main repo or Hobby zip).
2. Copy `voices/*.json` into a folder, e.g. `~/.e2t/voices/`.
3. Copy `templates/*_pro.md` next to skill templates or merge rules into your briefs.
4. Use:

```bash
e2t run <source> --voice pro_operator
# custom dir:
# set E2T_VOICE_DIR=~/.e2t/voices
```

Voice loader checks `E2T_VOICE_DIR` then built-ins.

## Support

See SUPPORT.md in the main repository. Attach `e2t version` output.
