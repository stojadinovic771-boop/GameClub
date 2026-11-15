# GameClub 1.0.0

The first public release of GameClub — a controller-first game launcher for Windows 10 / 11.
Project page: https://github.com/stojadinovic771-boop/GameClub

## Download

**`GameClub_Setup.exe`** (attached below). Run it and follow the steps.
GameClub isn't code-signed: if SmartScreen warns you, choose *More info* → *Run anyway*.

Upgrading from PadHub or GAMES? The installer offers to remove the old version first. Your settings, covers and play stats are kept.

## Highlights

- **Apps, PC Games and Emulation tabs** filled from a folder of shortcuts, with SteamGridDB covers.
- **Categories rail** (VIEW): categories from subfolders, Emulation systems detected automatically, or set by hand.
- **Game menu for emulators:** hold VIEW + START to resume or close an emulated game.
- **Controller everywhere:** desktop mouse, on-screen keyboard (VIEW + X), and optionally UAC prompts and the sign-in screen.
- **Bluetooth pairing without a keyboard** for controllers, and **headphone pairing** with automatic sound switching.
- **Controller battery** in the top bar.
- **Hidden mouse pointer** over full-screen games while you use the pad.
- Xbox / PlayStation / Nintendo button styles, accent colours, wallpaper background.

## Fixes in this release

- Emulation subfolders named after a system that contains the word "Game" (*GameCube*, *Game Boy*, *Game Gear*) were put in the PC Games tab — they now stay in Emulation.
- Startup tasks are only changed when you switch *Start with Windows* or *Controller on UAC & Sign-in* in Settings (fewer false alarms from Microsoft Defender).

## Known limits

- Windows only.
- Unsigned: Defender or SmartScreen may warn on first run.
- Controller on UAC & Sign-in needs the installed version (it runs as administrator) and works with XInput controllers.

## License

Free for personal and noncommercial use — [PolyForm Noncommercial 1.0.0](LICENSE.md).
