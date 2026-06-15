from pywinauto import Desktop

windows = Desktop(backend="uia").windows()

for w in windows:
    try:
        title = w.window_text()

        if "JioSaavn" in title:
            print("=" * 80)
            print("FOUND:", title)
            print("=" * 80)

            descendants = w.descendants()

            for i, ctrl in enumerate(descendants):
                try:
                    print(
                        f"{i}: "
                        f"Name='{ctrl.window_text()}' | "
                        f"Type='{ctrl.element_info.control_type}' | "
                        f"AutoID='{ctrl.element_info.automation_id}'"
                    )
                except:
                    pass

    except Exception as e:
        print(e)