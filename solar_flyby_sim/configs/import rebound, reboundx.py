import rebound, reboundx
sim = rebound.Simulation()
rx = reboundx.Extras(sim)

def check(name):
    try:
        rx.load_force(name)
        print(f"{name}: AVAILABLE")
    except Exception as e:
        print(f"{name}: MISSING -> {e}")

check("gr")
check("oblateness")
