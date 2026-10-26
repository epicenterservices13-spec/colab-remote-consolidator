# Imperial Colab Remote Consolidator & Purge Engine

## Overview
This repository provides automated, auditable, and non-destructive scripts to consolidate all satellite cloud remotes and Google Photos onto the primary 5 TiB master remote (`epic:`) using Google Colab's cloud compute, followed by verified purging of satellite remotes.

## Architectural Mandates
1. **Zero Data Loss**: Files are moved only when verified against destination, or transferred and checked before source deletion.
2. **Datacenter Throughput**: Executed via Google Colab VMs to prevent mobile battery drain, bandwidth choking, or Android process kills.
3. **Server-Side Across Configs**: For Google Drive-to-Google Drive moves (`turbo`, `brainrot`, `epicdev`, `longden`, `sneaky`, `tech`, `yola`), rclone leverages Google's server-side transfer API (`--drive-server-side-across-configs`) without re-downloading bytes over WAN.
4. **OneDrive Excision**: OneDrive assets are consolidated into `epic:od/`, dropping `onedrive:` usage below the 5.0 GiB boundary to prevent subscription charges.

## Remote Topography
| Remote | Type | Target Path on `epic:` | Transfer Mode |
|---|---|---|---|
| `onedrive:` | OneDrive Personal | `epic:od/` | Cross-cloud move (`--size-only --fast-list`) |
| `turbo:` | Google Drive | `epic:CONSOLIDATED_REMOTES/turbo/` | Server-side move (`--drive-server-side-across-configs`) |
| `brainrot:` | Google Drive | `epic:CONSOLIDATED_REMOTES/brainrot/` | Server-side move (`--drive-server-side-across-configs`) |
| `epicdev:` | Google Drive | `epic:CONSOLIDATED_REMOTES/epicdev/` | Server-side move (`--drive-server-side-across-configs`) |
| `longden:` | Google Drive | `epic:CONSOLIDATED_REMOTES/longden/` | Server-side move (`--drive-server-side-across-configs`) |
| `sneaky:` | Google Drive | `epic:CONSOLIDATED_REMOTES/sneaky/` | Server-side move (`--drive-server-side-across-configs`) |
| `tech:` | Google Drive | `epic:CONSOLIDATED_REMOTES/tech/` | Server-side move (`--drive-server-side-across-configs`) |
| `yola:` | Google Drive | `epic:CONSOLIDATED_REMOTES/yola/` | Server-side move (`--drive-server-side-across-configs`) |

## Verification Strategy
- Manifest tracking in `/content/consolidation.log`.
- Pre-move inventory generation.
- Empty directory elimination post-transfer (`--delete-empty-src-dirs`).
