# File ownership and updates

Separate a direct requested edit from installing ongoing generation ownership. Permission to improve a file permits a scoped patch; it does not silently make the file regenerable.

## Ownership

- `human`: preserve unrelated content and edit only within the requested scope.
- `managed-blocks`: regeneration owns only the marked sections.
- `generated`: regenerate only when the current file matches its recorded generated hash.
- `proposal`: a candidate outside the target path, used for unresolved semantic conflicts or work not yet authorized.

Before a generated refresh, read its manifest and current file. Recompute source evidence. Preserve changes outside managed sections. If managed content was edited elsewhere, resolve the conflict from evidence or leave a concrete proposal; do not silently select the generated version. Update ownership metadata only after the requested validation passes.

Optional block markers:

```text
<!-- agent-ready:start id=<stable-id> source=<evidence-ref> -->
...managed content...
<!-- agent-ready:end -->
```

Use unique stable IDs. Preserve newline style, project path conventions, and existing file placement. Prefer small patches and existing generation mechanisms over adding a new ownership framework.

## Assessment artifacts

`assess_project.py` requires an explicit new output directory outside the installed skill. It rejects existing directories and retains incomplete output after a failed stage for diagnosis. Retry into a new directory. Individual stage commands write to their explicit output paths; select fresh paths to preserve prior evidence.

The scripts do not implement managed refresh, a manifest engine, or conflict repair. These rules guide the acting agent; they do not describe automation already present.
