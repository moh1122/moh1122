# Moh El Masri — GitHub profile setup

Prepared for the public `moh1122/moh1122` repository and its `main` branch.

## Choose the version

- **The separate downloadable `README.md`:** a paste-only version. Its cards load from the public Summary Cards service and its recent-activity section links to GitHub. Replace the current README with it; no supporting files or workflow are needed.
- **This full package:** uses the five included SVG cards and can refresh both those cards and the recent-activity list daily. The repository-hosted cards remain available if the external generator is temporarily unavailable.

## Install the full package

1. Extract the ZIP.
2. Copy the contents of its `moh1122-profile/` folder into the root of your existing local `moh1122/moh1122` checkout. Replace `README.md` and keep the folder structure intact. On macOS, press **Command + Shift + .** in Finder to reveal the `.github` folder.
3. Review the changes and commit these paths: `README.md`, `profile-summary-card-output/`, `scripts/update_profile.py`, and `.github/workflows/update-profile.yml`.
4. Push your reviewed commit to `main`. You do not need GitHub Pages for a profile README.
5. In the repository's **Actions** tab, select **Update profile**, then **Run workflow** on `main`.
6. Check that the run succeeds and view <https://github.com/moh1122>.

If you prefer GitHub's web editor, upload `README.md` and the `profile-summary-card-output/` folder with **Add file → Upload files**. Create `scripts/update_profile.py` and `.github/workflows/update-profile.yml` with **Add file → Create new file**, pasting the corresponding contents. GitHub recognizes `/` in these filenames as folder separators. Commit the complete set to `main`, then run the workflow.

`SETUP.md` is for your reference and does not need to be committed.

## Daily refresh

The included workflow is scheduled for **08:23 UTC+3 / 05:23 UTC every day**. GitHub may delay scheduled jobs. It can also be started manually.

- No personal access token or paid service is required by the supplied code.
- The workflow uses GitHub's automatically provided `GITHUB_TOKEN` to read the public events endpoint and push changes to this repository.
- Its token has `contents: write` within this repository; no other permission is requested.
- Card generation receives only the public username, visual theme, and UTC offset. The GitHub token is never passed to that service.
- The workflow only runs for `moh1122/moh1122`. There is no push trigger, so refresh commits do not trigger another refresh.
- The action is pinned to the verified checkout v7.0.1 commit. Updating that pin later is a normal dependency maintenance choice.

If the run cannot push, check the repository's Actions policy and branch rules. Do not disable required branch protection just for this profile: use the paste-only README or adapt the workflow to open a pull request if direct bot commits are prohibited. If `main` changed while the run was executing, rerun it; the workflow does not force-push.

## What the numbers mean

These are GitHub's visible profile and repository metrics, as returned by the public Summary Cards generator. Language charts describe repository composition and commit activity; they do not represent every app in the App Store portfolio or measure proficiency. The service may cache results, so counts can differ temporarily from the live profile. Its documentation describes statistics based on up to 100 public repositories.

The recent-activity section uses the public events endpoint. It shows up to five selected events from the available recent window, excludes this profile repository, and combines repeated pushes to the same repository on the same day. It does not fetch private repository contents, issue text, or commit messages. Fewer than five entries is normal.

The five included SVGs were retrieved on **27 October 2026**. Refreshing is optional: the profile can display those saved snapshots immediately after upload. If a card request fails or returns invalid content, the script keeps the previous complete set. If the events API fails, it keeps the previous activity text. Warnings appear in the workflow log.

## Change the content

Edit the prose, links, app table, and technology list directly in `README.md`. Keep the two activity comments if you want automatic updates:

```html
<!--START_SECTION:activity-->
<!--END_SECTION:activity-->
```

The script updates only the text between those comments and the five SVG files. Change the profile username, card theme, or UTC offset in `scripts/update_profile.py` if you later adapt this for another account; also update the workflow repository guard and README links.

## Sources and credits

- Layout inspiration: <https://github.com/Panniantong/Panniantong>
- Current profile: <https://github.com/moh1122/moh1122>
- Portfolio and published project details: <https://iosapps.cloud>
- GitHub Profile Summary Cards: <https://github.com/vn7n24fzkq/github-profile-summary-cards>
- Badges: <https://shields.io>
- GitHub profile README requirements: <https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme>
- Public events API: <https://docs.github.com/en/rest/activity/events>
- Workflow scheduling: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule>

The profile wording and refresh script were prepared specifically for Moh El Masri. The stats SVGs are generated by GitHub Profile Summary Cards. No third-party README biography or project claims have been copied.
