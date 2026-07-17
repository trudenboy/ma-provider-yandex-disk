---
title: Browse and library sync
sidebar:
  order: 1
---

The provider exposes the contents of the selected Yandex Disk folder to
Music Assistant in two ways: live folder browsing (Browse) and a full
library sync.

## Browse

The Browse tab shows the Disk's folder structure starting from the root
folder set in the configuration (e.g. `disk:/Music`). Audio files can be
played straight from the tree without waiting for a sync. Folder listings
are cached for 5 minutes.

## Library sync

A sync walks the whole root folder and fills the Music Assistant library
with tracks, albums, artists and playlists — metadata is read from the
files' own tags, just like the regular filesystem provider.

- Changes are detected via each file's `md5`: subsequent syncs only process
  new and modified files.
- Syncs always fetch fresh folder listings, bypassing the cache.
- The instance's content type (music / audiobooks / podcasts) defines how
  files are indexed.

## Multiple instances

Several instances can run side by side — e.g. different Yandex accounts, or
different folders of the same Disk (music in one, audiobooks in another).
