import math

# v4 legs (ggldnl Hexapod-Hardware geometry, mm). Body frame: origin on the femur-joint plane,
# x forward, y left, z up. The battery bottom sits 37mm below the origin.
COXA = 68.0
FEMUR = 76.7
TIBIA = 101.0   # bare tibia tip (99.9) + grip tape; was 104.6 with the TPU foot
AXIS_Z = 0.0

LEGS = {
    "FL": (82.0, 57.0, 45.0),
    "ML": (0.0, 71.0, 90.0),
    "RL": (-82.0, 57.0, 135.0),
    "RR": (-82.0, -57.0, -135.0),
    "MR": (0.0, -71.0, -90.0),
    "FR": (82.0, -57.0, -45.0),
}
TRIPOD_A = ("FL", "MR", "RL")
TRIPOD_B = ("ML", "RR", "FR")

# Tibia 0 = perpendicular to the femur, measured to the taped tibia tip. The URDF tibia joint reads this angle minus 73.
# Ranges: coxa kept clear of the neighbouring legs, tibia = the URDF's -125..0.
LIMITS = {"coxa": (-35.0, 35.0), "femur": (-80.0, 85.0), "tibia": (-52.0, 73.0)}
TIBIA_URDF_OFFSET = -73.0


def leg_ik(leg, x, y, z):
    """Foot position in the body frame -> (coxa, femur, tibia) in degrees."""
    mx, my, g = LEGS[leg]
    g = math.radians(g)
    dx, dy = x - mx, y - my
    lx = dx * math.cos(g) + dy * math.sin(g)
    ly = -dx * math.sin(g) + dy * math.cos(g)
    coxa = math.atan2(ly, lx)

    dr, dz = math.hypot(lx, ly) - COXA, z - AXIS_Z
    reach = math.hypot(dr, dz)
    cos_knee = (FEMUR ** 2 + reach ** 2 - TIBIA ** 2) / (2 * FEMUR * reach)
    cos_knee = max(-1.0, min(1.0, cos_knee))
    femur = math.atan2(dz, dr) + math.acos(cos_knee)
    kr, kz = FEMUR * math.cos(femur), FEMUR * math.sin(femur)
    tibia = femur - math.pi / 2 - math.atan2(dz - kz, dr - kr)
    return math.degrees(coxa), math.degrees(femur), math.degrees(tibia)


def leg_fk(leg, coxa, femur, tibia):
    mx, my, g = LEGS[leg]
    c, f, t = map(math.radians, (coxa, femur, tibia))
    psi = f - t - math.pi / 2
    r = COXA + FEMUR * math.cos(f) + TIBIA * math.cos(psi)
    z = AXIS_Z + FEMUR * math.sin(f) + TIBIA * math.sin(psi)
    a = math.radians(LEGS[leg][2]) + c
    return mx + r * math.cos(a), my + r * math.sin(a), z


def out_of_range(angles):
    return [name for name, v in zip(("coxa", "femur", "tibia"), angles)
            if not LIMITS[name][0] - 0.5 <= v <= LIMITS[name][1] + 0.5]
