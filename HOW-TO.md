# GitHub profile: setup (about 10 minutes)

1. On GitHub, create a **public** repo named exactly `Taver-Versch` (same as your username). GitHub shows
   its README on your profile.
2. Upload `README.md`, the `assets` folder and the `.github` folder (use GitHub Desktop or drag the folders in,
   so the hidden `.github` folder comes along). `make_header.py` and `fonts` can go up too,
   they're only needed to rebuild the header.
3. Go to the repo's **Actions** tab, pick **Generate stats**, and click **Run workflow**. When it's done, the
   terminal at the top of your profile fills in, stats included, and it refreshes every 6 hours.

## Changing the header
The terminal lines are at the top of `make_header.py` (`LINES`). Edit them and push; the workflow rebuilds the terminal (header + stats) into the `output` branch.

The header's font is baked into the SVG, so it doesn't depend on any outside
service. The workflow runs `make_stats.py`, which adds the `gh stats` block to the header.
