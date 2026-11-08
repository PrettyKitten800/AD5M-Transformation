// Upgrade BOM for VORON1.8 -> Trident upgrade path. Populate with 1.8 delta parts.
var upgrade_bom = {
    "Fasteners": {},
    "Motion": {},
    "Vibration Management": {},
    "Electronics": {},
    "Misc": {},
    "Cables": {}
};

// Upgrade BOM for Trident R1 -> Trident R2 upgrade path.
var upgrade_bom_trident = {
    "Fasteners": {
        "2020 Drop-in T-nut, M3": 8,
        "M3xD5xL4 Heat Set": 30,
        "M3 Washer": 1,
        "M3x12 SHCS": 10,
        "M3x16 SHCS": 11,
        "M3x25 SHCS": 4,
        "M3x40 SHCS": 6,
        "M3x6 BHCS": 28,
        "M5 1mm Spacer": 2,
        "M5xD7xL6 Heat Set": 15,
        "M5x16 BHCS": 16,
        "M5x40 BHCS": 4
    },
    "Motion": {
        "F695 Bearing (short stepper shaft motors: 4)": 6
    },
    "Misc": {
        "Single Sided Foam Tape (3mm Thick, 5-6mm Wide)": 3
    }
};

var bom = {
    "Fasteners": {
        "2020 Drop-in T-nut, M5": 69,
        "M5x40 BHCS": 4,
        "M5x30 BHCS": 4,
        "M5x16 BHCS": 43,
        "M5x10 BHCS": 45,
        "M5 1mm Spacer": 24,
        "M5xD7xL6 Heat Set": 15,
        "M4x6 BHCS": 7,
        "M4 Knurled Nut": 3,
        "M3x50 SHCS": 2,
        "M3x40 SHCS": 9,
        "M3x30 SHCS": 9,
        "M3x25 SHCS": 10,
        "M3x20 SHCS": 0,
        "M3x16 SHCS": 27,
        "M3x12 SHCS": 73,
        "M3x8 SHCS": 84,
        "M3x6 BHCS": 59,
        "M3x10 FHCS": 2,
        "M3x6 FHCS": 17,
        "M3 Locknut": 6,
        "M3 Washer": 4,
        "2020 Drop-in T-nut, M3": 32,
        "M3 Hammerhead T-Nut": 55,
        "M3xD5xL4 Heat Set": 100,
        "M2x10 Selftapping screw": 17
    },
    "Motion": {
        "GT2 20T Pulley (5mm ID 6mm W)": 3,
        "GT2 20T Toothed Idler (5mm ID 6mm W)": 2,
        "F695 Bearing": 26,
        "GE5C Spherical Bearing": 3,
        "TR8x4 Leadscrew Nut": 3,
        "5x30mm Shaft": 1
    },
    "Vibration Management": {
        "Rubber Foot": 4
    },
    "Electronics": {
        "NEMA17 Motor 17HS19-2004S": 2,
        "SPDT KW10 Limit Micro Switch": 3,
        "Omron TL-Q5MC2 - NPN, NC, 5mm Sense Inductive Probe": 1,
        "E3D V6 Bowden Hotend Kit (24V)": 1,
        "50x50x15 Centrifugal Fan (24V)": 1,
        "40x40x10 Axial Fan (24V)": 1,
        "Mini 12864 Display": 1,
        "Medium Blow Fuse 5 x 20mm: 4A for 220V mains or 8A for 120v": 2,
        "TycoElectronics 10EGG1-2 Filtered Power Inlet": 1,
        "ZF - Rocker Switches DPST 16A": 1,
        "Keystone CAT6 Insert (Optional)": 1,
        "60x60x20 Fan (24V)": 3,
        "6 Stepper Controller (or multiple to equal 6+ steppers)": 1,
        "TMC2209 Stepper Motor Driver": 6,
        "Raspberry Pi 4": 1,
        "Mean Well LRS-200-24 PSU": 1,
        "Mean Well TBC-09 Terminal Cover": 1,
        "Mean Well RS-25-5 PSU": 1,
        "Omron G3A-210B-DC5 SSR": 1,
        "DIN Rail Mount Bracket for G3A SSR": 1,
        "BAT85 Diode": 1,
        "C13 Power Cord": 1,
        "Thermal Fuse (150C)": 1
    },
    "Misc": {
        "PTFE Tube (4mm OD 2mm ID; Toolhead) - 1m": 1,
        "3M VHB Tape 5952": 1,
        "Single Sided Foam Tape (3mm Thick, 5-6mm Wide)": 9,
        "Loctite Blue Threadlocker Stick": 1,
        "Mobil EP2 Grease": 1,
        "Tesa Wire Loom Harness Tape": 1,
        "6x3mm Neodymium Magnet": 8
    },
    "Cables": {
        "Nylon Cable Ties 4\"": 40,
        "1/2\" Braided Cable Sheathing (ft)": 5,
        "18AWG High-Flex Wire (ft)": 10,
        "20AWG High-Flex Wire (ft)": 10,
        "22-24AWG High-Flex Wire (min 19 strand)(ft)": 100,
        "Spade Crimp Terminal 4.8mm Female": 10,
        "JST XH Connector Plug 4 Position": 5,
        "JST XH Connector Plug 3 Position": 4,
        "JST XH Connector Plug 2 Position": 2,
        "JST XH Female Pin": 40,
        "MicroFit3 Connector Plug 4 Position": 2,
        "MicroFit3 Connector Plug 3 Position": 1,
        "MicroFit3 Connector Plug 2 Position": 5,
        "MicroFit3 Connector Receptacle 4 Position": 2,
        "MicroFit3 Connector Receptacle 3 Position": 1,
        "MicroFit3 Connector Receptacle 2 Position": 5,
        "MicroFit3 Female Pin": 40,
        "MicroFit3 Male Pin": 40,
        "10x11 Cable Chain - 1m, 3 End Sets": 1,
        "WAGO 221-415 Lever-Nuts": 3,
        "WAGO 221-412 Lever-Nuts": 3,
    }
};
