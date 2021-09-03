import sys


def getArguments() -> dict:
    """
    Reads the command line arguments passed to this script and returns a dictionary with the following keys ->
    - "controller" -> Opendaylight Controller IP [type: string]
    - "hosts" -> Number of hosts [type: number]
    - "switches" -> Number of switches [type: number]
    - "bw" -> Bandwidth range: [type: tuple[number, number]]
    - "delay"-> Link delay range: [type: tuple[number, number]]
    """

    n = len(sys.argv)

    if n == 1:
        print("Passing the --controller argument is mandatory")
        exit(1)

    arguments: dict = {
        "controller": None,
        "hosts": 12,
        "switches": 4,
        "bw": (0, 5),
        "delay": (2, 30),
    }

    for arg in sys.argv[1:]:
        option: list[str] = arg.split("=")

        if option[0] == "--controller":
            arguments["controller"] = option[1]
        elif option[0] == "--hosts":
            arguments["hosts"] = int(option[1])
        elif option[0] == "--switches":
            arguments["switches"] = int(option[1])
        elif option[0] == "--bw":
            bwRange = option[1].split(",")
            arguments["bw"] = (int(bwRange[0]), int(bwRange[1]))
        elif option[0] == "--delay":
            delay = option[1].split(",")
            arguments["delay"] = (int(delay[0]), int(delay[1]))

    return arguments
