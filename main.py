import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Global plot settings

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 16,
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "legend.fontsize": 13,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "figure.dpi": 120,
    "savefig.dpi": 600
})

# Constants

MU_DRY = 0.7
MU_WET = 0.4

REACTION_DAY = 1.5
REACTION_NIGHT = 3.5

PHONE_DELAY = 0.3

LOW_BEAM_VISIBILITY = 60
HIGH_BEAM_VISIBILITY = 150

# Functions

def efficiency_from_mass(mass_tons):

    eta_b = max(0.5, 1.0 - 0.02 * mass_tons)
    eta_t = max(0.6, 1.0 - 0.01 * mass_tons)

    return eta_b, eta_t


def brake_delay_from_category(category):

    if category == "Passenger Cars":
        return 0.3

    elif category == "SUV / Van":
        return 0.4

    elif category == "Light Truck":
        return 0.5

    elif category == "Medium Truck":
        return 0.7

    elif category == "Bus":
        return 0.5

    else:
        return 1.0


def classify_vehicle_category(mass_kg):

    if mass_kg < 2200:
        return "Passenger Cars"

    elif mass_kg < 3500:
        return "SUV / Van"

    elif mass_kg < 7500:
        return "Light Truck"

    elif mass_kg < 16000:
        return "Medium Truck"

    elif mass_kg < 22000:
        return "Bus"

    else:
        return "Heavy Truck"


def total_distance(speed_kmh, mass_kg, reaction_time, mu):

    v = speed_kmh / 3.6
    mass_tons = mass_kg / 1000

    eta_b, eta_t = efficiency_from_mass(mass_tons)

    category = classify_vehicle_category(mass_kg)

    brake_delay = brake_delay_from_category(category)

    reaction = v * reaction_time
    delay = v * brake_delay

    braking = (v ** 2) / (2 * mu * 9.81 * eta_b * eta_t)

    return reaction + delay + braking


# Vehicle data

vehicles = {

    "Honda Fit": 1500,
    "Toyota Vitz": 1400,
    "Toyota Aqua": 1500,
    "Nissan Note": 1550,
    "Suzuki Swift": 1450,
    "Nissan Tiida": 1800,
    "Mazda Axela": 1900,
    "Toyota Premio": 1900,
    "Honda Civic": 1850,

    "Honda CR-V": 2200,
    "Nissan X-Trail": 2300,
    "Toyota RAV4": 2200,
    "Mazda CX-5": 2300,
    "Subaru Forester": 2300,
    "Toyota Hiace": 3200,
    "Nissan Caravan": 3200,
    "Toyota Hilux": 3000,
    "Nissan Navara": 3200,
    "Isuzu D-Max": 3000,
    "Mitsubishi Triton": 3100,
    "Land Rover": 3000,

    "Light Truck": 9000,
    "Medium Truck": 13000,
    "Bus (Higer)": 19000,
    "Heavy Truck": 30000
}

# Speed range

speeds = list(range(20, 141, 10))

# Group vehicles

categories = defaultdict(list)

for name, mass in vehicles.items():

    cat = classify_vehicle_category(mass)

    categories[cat].append(mass)

# Category labels with average mass

category_labels = {}

for category, masses in categories.items():

    avg_mass = int(sum(masses) / len(masses))

    category_labels[category] = f"{category} ({avg_mass} kg)"

# Category data sheet

rows = []

for category, masses in categories.items():

    for speed in speeds:

        day_dry = [
            total_distance(speed, m, REACTION_DAY, MU_DRY)
            for m in masses
        ]

        night_dry = [
            total_distance(speed, m, REACTION_NIGHT, MU_DRY)
            for m in masses
        ]

        day_wet = [
            total_distance(speed, m, REACTION_DAY, MU_WET)
            for m in masses
        ]

        night_wet = [
            total_distance(speed, m, REACTION_NIGHT, MU_WET)
            for m in masses
        ]

        rows.append({
            "Category": category,
            "Speed (km/h)": speed,
            "Day Dry (m)": round(sum(day_dry)/len(day_dry), 2),
            "Night Dry (m)": round(sum(night_dry)/len(night_dry), 2),
            "Day Wet (m)": round(sum(day_wet)/len(day_wet), 2),
            "Night Wet (m)": round(sum(night_wet)/len(night_wet), 2)
        })

df = pd.DataFrame(rows)

df.to_excel("outputs/tables/all_conditions_category_distances.xlsx", index=False)

print("Saved: all_conditions_category_distances.xlsx")

# Vehicle-level data sheet

vehicle_rows = []

for name, mass in vehicles.items():

    for speed in speeds:

        vehicle_rows.append({

            "Vehicle": name,
            "Mass (kg)": mass,
            "Category": classify_vehicle_category(mass),
            "Speed (km/h)": speed,

            "Day Dry (m)": round(
                total_distance(speed, mass, REACTION_DAY, MU_DRY), 2
            ),

            "Night Dry (m)": round(
                total_distance(speed, mass, REACTION_NIGHT, MU_DRY), 2
            ),

            "Day Wet (m)": round(
                total_distance(speed, mass, REACTION_DAY, MU_WET), 2
            ),

            "Night Wet (m)": round(
                total_distance(speed, mass, REACTION_NIGHT, MU_WET), 2
            )
        })

vehicle_df = pd.DataFrame(vehicle_rows)

vehicle_df.to_excel("outputs/tables/vehicle_level_distances.xlsx", index=False)

print("Saved: vehicle_level_distances.xlsx")

# Colors

base_colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))

# Graph 0 — Baseline mass comparison

plt.figure(figsize=(18, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    distances = []

    for speed in speeds:

        vals = [
            total_distance(speed, m, REACTION_DAY, MU_DRY)
            for m in masses
        ]

        distances.append(sum(vals)/len(vals))

    plt.plot(
        speeds,
        distances,
        label=category_labels[category],
        linewidth=3,
        color=color
    )

plt.title("Stopping Distance by Vehicle Category (Day, Dry Conditions)")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(loc='upper left', framealpha=0.9)

plt.grid()

plt.savefig("outputs/graphs/baseline_mass_comparison.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/baseline_mass_comparison.svg", bbox_inches='tight')

plt.show()

# Graph 1 — Dry conditions

plt.figure(figsize=(20, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    day_vals = []
    night_vals = []

    for speed in speeds:

        day = [
            total_distance(speed, m, REACTION_DAY, MU_DRY)
            for m in masses
        ]

        night = [
            total_distance(speed, m, REACTION_NIGHT, MU_DRY)
            for m in masses
        ]

        day_vals.append(sum(day)/len(day))
        night_vals.append(sum(night)/len(night))

    plt.plot(
        speeds,
        day_vals,
        label=f"{category_labels[category]} — Day",
        linewidth=3,
        color=color
    )

    plt.plot(
        speeds,
        night_vals,
        label=f"{category_labels[category]} — Night",
        linewidth=3,
        linestyle="--",
        color=color
    )

plt.title("Stopping Distance by Category Under Dry Conditions")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(ncol=2, framealpha=0.9)

plt.grid()

plt.savefig("outputs/graphs/dry_conditions_day_vs_night.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/dry_conditions_day_vs_night.svg", bbox_inches='tight')

plt.show()

# Graph 2 — Wet conditions

plt.figure(figsize=(20, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    day_vals = []
    night_vals = []

    for speed in speeds:

        day = [
            total_distance(speed, m, REACTION_DAY, MU_WET)
            for m in masses
        ]

        night = [
            total_distance(speed, m, REACTION_NIGHT, MU_WET)
            for m in masses
        ]

        day_vals.append(sum(day)/len(day))
        night_vals.append(sum(night)/len(night))

    plt.plot(
        speeds,
        day_vals,
        label=f"{category_labels[category]} — Day",
        linewidth=3,
        color=color
    )

    plt.plot(
        speeds,
        night_vals,
        label=f"{category_labels[category]} — Night",
        linewidth=3,
        linestyle="--",
        color=color
    )

plt.title("Stopping Distance by Category Under Wet Conditions")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(ncol=2, framealpha=0.9)

plt.grid()

plt.savefig("outputs/graphs/wet_conditions_day_vs_night.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/wet_conditions_day_vs_night.svg", bbox_inches='tight')

plt.show()

# Graph 3 — Mass-speed divergence

plt.figure(figsize=(18, 10))

representative_vehicles = {
    "Passenger Car (~1500 kg)": 1500,
    "Bus (~19000 kg)": 19000,
    "Heavy Truck (~30000 kg)": 30000
}

colors = ["#1f77b4", "#ff7f0e", "#d62728"]

for (label, mass), color in zip(representative_vehicles.items(), colors):

    distances = []

    for speed in speeds:

        d = total_distance(speed, mass, REACTION_DAY, MU_DRY)

        distances.append(d)

    plt.plot(
        speeds,
        distances,
        label=label,
        linewidth=4,
        color=color
    )

plt.title("Effect of Vehicle Mass on Stopping Distance at Increasing Speeds")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend()

plt.grid()

plt.savefig("outputs/graphs/mass_speed_divergence.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/mass_speed_divergence.svg", bbox_inches='tight')

plt.show()

# Graph 4 — Individual category comparisons

for (category, masses), color in zip(categories.items(), base_colors):

    plt.figure(figsize=(18, 10))

    day_dry = []
    night_dry = []

    day_wet = []
    night_wet = []

    for speed in speeds:

        dd = [
            total_distance(speed, m, REACTION_DAY, MU_DRY)
            for m in masses
        ]

        nd = [
            total_distance(speed, m, REACTION_NIGHT, MU_DRY)
            for m in masses
        ]

        dw = [
            total_distance(speed, m, REACTION_DAY, MU_WET)
            for m in masses
        ]

        nw = [
            total_distance(speed, m, REACTION_NIGHT, MU_WET)
            for m in masses
        ]

        day_dry.append(sum(dd)/len(dd))
        night_dry.append(sum(nd)/len(nd))

        day_wet.append(sum(dw)/len(dw))
        night_wet.append(sum(nw)/len(nw))

    plt.plot(
        speeds,
        day_dry,
        label="Day Dry",
        linewidth=3,
        color=color
    )

    plt.plot(
        speeds,
        night_dry,
        label="Night Dry",
        linewidth=3,
        linestyle="--",
        color=color
    )

    plt.plot(
        speeds,
        day_wet,
        label="Day Wet",
        linewidth=3,
        color="black"
    )

    plt.plot(
        speeds,
        night_wet,
        label="Night Wet",
        linewidth=3,
        linestyle="--",
        color="black"
    )

    plt.title(f"{category}: All Conditions Comparison")

    plt.xlabel("Speed (km/h)")
    plt.ylabel("Stopping Distance (m)")

    plt.legend(framealpha=0.9)

    plt.grid()

    filename = category.replace(" ", "_").replace("/", "")

    plt.savefig(f"outputs/graphs/{filename}_comparison.pdf", bbox_inches='tight')
    plt.savefig(f"outputs/graphs/{filename}_comparison.svg", bbox_inches='tight')

    plt.show()

# Graph 5 — Phone effect during daytime

plt.figure(figsize=(18, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    normal_vals = []
    phone_vals = []

    for speed in speeds:

        normal = [
            total_distance(speed, m, REACTION_DAY, MU_DRY)
            for m in masses
        ]

        phone = [
            total_distance(speed, m, REACTION_DAY + PHONE_DELAY, MU_DRY)
            for m in masses
        ]

        normal_vals.append(sum(normal)/len(normal))
        phone_vals.append(sum(phone)/len(phone))

    plt.plot(
        speeds,
        normal_vals,
        label=f"{category_labels[category]} — Normal",
        linewidth=3,
        color=color
    )

    plt.plot(
        speeds,
        phone_vals,
        label=f"{category_labels[category]} — Phone",
        linewidth=3,
        linestyle="--",
        color=color
    )

plt.title("Effect of Handsfree Phone Use on Stopping Distance (Day)")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(ncol=2)

plt.grid()

plt.savefig("outputs/graphs/phone_effect_day.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/phone_effect_day.svg", bbox_inches='tight')

plt.show()

# Graph 6 — Phone effect during nighttime

plt.figure(figsize=(18, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    normal_vals = []
    phone_vals = []

    for speed in speeds:

        normal = [
            total_distance(speed, m, REACTION_NIGHT, MU_DRY)
            for m in masses
        ]

        phone = [
            total_distance(speed, m, REACTION_NIGHT + PHONE_DELAY, MU_DRY)
            for m in masses
        ]

        normal_vals.append(sum(normal)/len(normal))
        phone_vals.append(sum(phone)/len(phone))

    plt.plot(
        speeds,
        normal_vals,
        label=f"{category_labels[category]} — Normal",
        linewidth=3,
        color=color
    )

    plt.plot(
        speeds,
        phone_vals,
        label=f"{category_labels[category]} — Phone",
        linewidth=3,
        linestyle="--",
        color=color
    )

plt.title("Effect of Handsfree Phone Use on Stopping Distance (Night)")

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(ncol=2)

plt.grid()

plt.savefig("outputs/graphs/phone_effect_night.pdf", bbox_inches='tight')
plt.savefig("outputs/graphs/phone_effect_night.svg", bbox_inches='tight')

plt.show()

# Graph 7 — Nighttime visibility risk analysis

plt.figure(figsize=(20, 10))

for (category, masses), color in zip(categories.items(), base_colors):

    dry_vals = []
    wet_vals = []

    for speed in speeds:

        dry = [
            total_distance(speed, m, REACTION_NIGHT, MU_DRY)
            for m in masses
        ]

        wet = [
            total_distance(speed, m, REACTION_NIGHT, MU_WET)
            for m in masses
        ]

        dry_vals.append(sum(dry) / len(dry))
        wet_vals.append(sum(wet) / len(wet))

    # DRY ROAD
    plt.plot(
        speeds,
        dry_vals,
        label=f"{category_labels[category]} — Dry",
        linewidth=3,
        color=color
    )

    # WET ROAD
    plt.plot(
        speeds,
        wet_vals,
        label=f"{category_labels[category]} — Wet",
        linewidth=3,
        linestyle="--",
        color=color
    )

# LOW BEAM VISIBILITY

plt.axhline(
    y=LOW_BEAM_VISIBILITY,
    color='black',
    linestyle=':',
    linewidth=4,
    label="Low-Beam Visibility (~60 m)"
)

# HIGH BEAM VISIBILITY

plt.axhline(
    y=HIGH_BEAM_VISIBILITY,
    color='red',
    linestyle=':',
    linewidth=4,
    label="High-Beam Visibility (~150 m)"
)

plt.title(
    "Nighttime Stopping Distance Relative to Headlight Visibility Thresholds"
)

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(ncol=2, framealpha=0.9)

plt.grid()

plt.savefig(
    "outputs/graphs/night_visibility_risk_analysis.pdf",
    bbox_inches='tight'
)

plt.savefig(
    "outputs/graphs/night_visibility_risk_analysis.svg",
    bbox_inches='tight'
)

plt.show()

# ================= GRAPH 8: HEAVY TRUCK NIGHT VISIBILITY ANALYSIS =================

plt.figure(figsize=(16, 9))

heavy_truck_masses = categories["Heavy Truck"]

dry_vals = []
wet_vals = []

for speed in speeds:

    dry = [
        total_distance(speed, m, REACTION_NIGHT, MU_DRY)
        for m in heavy_truck_masses
    ]

    wet = [
        total_distance(speed, m, REACTION_NIGHT, MU_WET)
        for m in heavy_truck_masses
    ]

    dry_vals.append(sum(dry) / len(dry))
    wet_vals.append(sum(wet) / len(wet))

# Heavy truck curves
plt.plot(
    speeds,
    dry_vals,
    linewidth=4,
    label="Heavy Truck — Dry Road",
)

plt.plot(
    speeds,
    wet_vals,
    linewidth=4,
    linestyle="--",
    label="Heavy Truck — Wet Road",
)

# Low beam visibility line
plt.axhline(
    y=LOW_BEAM_VISIBILITY,
    color="black",
    linestyle=":",
    linewidth=4,
    label="Low Beam Visibility (60 m)"
)

# High beam visibility line
plt.axhline(
    y=HIGH_BEAM_VISIBILITY,
    color="red",
    linestyle=":",
    linewidth=4,
    label="High Beam Visibility (90 m)"
)

plt.title(
    "Heavy Truck Night Stopping Distance vs Headlight Visibility"
)

plt.xlabel("Speed (km/h)")
plt.ylabel("Stopping Distance (m)")

plt.legend(framealpha=0.95)
plt.grid()

plt.savefig(
    "outputs/graphs/heavy_truck_visibility_analysis.pdf",
    bbox_inches='tight'
)

plt.savefig(
    "outputs/graphs/heavy_truck_visibility_analysis.svg",
    bbox_inches='tight'
)

plt.show()
print("\nALL FILES GENERATED SUCCESSFULLY")