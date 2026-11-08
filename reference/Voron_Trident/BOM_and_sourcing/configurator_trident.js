function update_printer_geometry(update_type) {
    var build_x = parseInt($("#build-x").val());
    var build_y = parseInt($("#build-y").val());
    var build_z = parseInt($("#build-z").val());

    var frame_x = parseInt($("#frame-x").val());
    var frame_y = parseInt($("#frame-y").val());
    var frame_z = parseInt($("#frame-z").val());

    if (update_type == "build") {
        // Recalculate the frame
        frame_x = build_x + 160;
        frame_y = build_y + 160;
        frame_z = build_z + 250;
        $("#frame-x").val(frame_x);
        $("#frame-y").val(frame_y);
        $("#frame-z").val(frame_z);
    } else {
        // Recalculate the build volume
        build_x = frame_x - 160;
        build_y = frame_y - 160;
        build_z = frame_z - 250;
        $("#build-x").val(build_x);
        $("#build-y").val(build_y);
        $("#build-z").val(build_z);
    }
}

function update_final_stats() {
    var size_option = $('input[name=size-options]:checked').val();
    if (size_option != "custom") {
        size_option = parseInt(size_option);
        size_z = 250;
        $("#build-x").val(size_option);
        $("#build-y").val(size_option);
        $("#build-z").val(size_z);
        update_printer_geometry("build");
    }
    var stats_html = "<br>";
    stats_html += $("#build-x").val() + " mm<br>";
    stats_html += $("#build-y").val() + " mm<br>";
    stats_html += $("#build-z").val() + " mm<br>";
    stats_html += "<br>";
    stats_html += $("#frame-x").val() + " mm<br>";
    stats_html += $("#frame-y").val() + " mm<br>";
    stats_html += $("#frame-z").val() + " mm<br>";
    $("#printer-stats").html(stats_html);
    populate_bom();
    $("#bom-btn").attr("href", generate_bom_csv());
    $("#page-bom").html(generate_bom_table());
}

function populate_bom() {
    var build_x = parseInt($("#build-x").val());
    var build_y = parseInt($("#build-y").val());
    var build_z = parseInt($("#build-z").val());

    var frame_x = parseInt($("#frame-x").val());
    var frame_y = parseInt($("#frame-y").val());
    var frame_z = parseInt($("#frame-z").val());

    var joint = $('input[name=joint-options]:checked').val();
    var build_type = $('input[name=upgrade-options]:checked').val();
    var feed = $('input[name=feed-options]:checked').val();

    if (build_type == "upgrade") {
        bom = upgrade_bom;
    } else if (build_type == "upgrade_trident") {
        bom = upgrade_bom_trident;
        return;
    }

    var x_frame_extrusion = frame_x - 40;
    var y_frame_extrusion = frame_y - 40;
    var z_frame_extrusion = frame_z;
    if (joint != "blind") {
        z_frame_extrusion = frame_z - 40;
    }

    var x_gantry_extrusion = x_frame_extrusion - 40;

    var x_rail = build_x + 50;
    var y_rail = build_y + 50;
    var z_rail = build_z + 50;
    var leadscrew = z_rail;

    bom["Frame"] = {}; // init Frame

    // DIN rails
    bom["Frame"]["DIN 3 Rails (35mm W) - " + x_frame_extrusion + "mm"] = 2

    // Feed 
    if (feed == "direct") {
        bom["Fasteners"]["M3xD5xL4 Heat Set"] += 9;
        bom["Fasteners"]["M3x20 SHCS"] += 3;
        bom["Fasteners"]["M3x30 SHCS"] += 4;
        bom["Fasteners"]["M3x8 SHCS"] += 2;
        bom["Motion"]["BMG Extruder Components Kit"] = 1;
        bom["Electronics"]["NEMA14 Motor 36STH20-1004AHG"] = 1;
        bom["Electronics"]["NeoPixel RGBW Mini Button PCB"] = 3;
    } else {
        bom["Fasteners"]["M3xD5xL4 Heat Set"] += 4;
        bom["Fasteners"]["M3x20 SHCS"] += 2;
        bom["Fasteners"]["M3x30 SHCS"] += 2;
    }

    // Feed tube
    var feed_tube_length = frame_y + 200;
    if (feed == "direct") {
        bom["Misc"]["PTFE Tube (4mm OD 3mm ID) - 1m"] = 1
    } else {
        if (build_type != "upgrade") {
            bom["Misc"]["PTFE Tube (4mm OD 2mm ID) - 1m"] = 1
        }
    }

    // Rails
    bom["Motion"]["Linear Rail MGN12H " + x_rail + "mm"] = 0;
    bom["Motion"]["Linear Rail MGN9H " + y_rail + "mm"] = 0;
    bom["Motion"]["Linear Rail MGN9H " + z_rail + "mm"] = 0;

    bom["Motion"]["Linear Rail MGN12H " + x_rail + "mm"] += 1;
    bom["Fasteners"]["M3x8 SHCS"] += get_screws_per_rail(x_rail);
    bom["Fasteners"]["2020 Drop-in T-nut, M3"] += get_screws_per_rail(x_rail);

    bom["Motion"]["Linear Rail MGN9H " + y_rail + "mm"] += 2;
    bom["Fasteners"]["M3x8 SHCS"] += get_screws_per_rail(y_rail) * 2;
    bom["Fasteners"]["2020 Drop-in T-nut, M3"] += get_screws_per_rail(y_rail) * 2;

    bom["Motion"]["Linear Rail MGN9H " + z_rail + "mm"] += 3;
    bom["Fasteners"]["M3x8 SHCS"] += get_screws_per_rail(z_rail) * 3;
    bom["Fasteners"]["2020 Drop-in T-nut, M3"] += get_screws_per_rail(z_rail) * 3;

    bom["Electronics"]["NEMA17 TR8x4 " + leadscrew + "mm Linear Stepper"] = 3;

    // Extrusions
    var cross_brace_extrusion = build_x - 10;
    bom["Frame"]["Misumi HFSB5-2020-" + cross_brace_extrusion] = 1;
    bom["Frame"]["Misumi HFSB5-2020-" + x_frame_extrusion + "-TPW"] = 0;
    bom["Frame"]["Misumi HFSB5-2020-" + y_frame_extrusion + "-TPW"] = 0;

    // Rear Z Rail Mount
    bom["Frame"]["Misumi HFSB5-2020-" + (build_z + 80) + "-LTP"] = 1

    // Y rail mounts
    bom["Frame"]["Misumi HFSB5-2020-" + y_frame_extrusion + "-TPW"] += 2;

    // X Gantry
    bom["Frame"]["Misumi HFSB5-2020-" + x_gantry_extrusion] = 1;

    if (joint == "blind") {
        bom["Frame"]["Misumi HFSB5-2020-" + z_frame_extrusion + "-LCP-RCP-AV" + (z_frame_extrusion - 140)] = 4;
        bom["Fasteners"]["M5x16 BHCS"] += 14;
    } else if (joint == "misumi") {
        bom["Frame"]["Misumi HFSB5-2020-" + z_frame_extrusion + "-AV" + (z_frame_extrusion - 120) + "-TPW"] = 4;
        bom["Frame"]["Misumi HBLCR5-B"] = 8;
        bom["Fasteners"]["2020 Drop-in T-nut, M5"] += 2;
        bom["Fasteners"]["M5x16 BHCS"] += 2;
    } else {
        bom["Frame"]["Misumi HFSB5-2020-" + z_frame_extrusion + "-AV" + (z_frame_extrusion - 120) + "-TPW"] = 4;
        bom["Fasteners"]["M5x16 BHCS"] += 14;
        bom["Frame"]["OpenBuilds Cube Corner Connector"] = 8;
    }

    bom["Frame"]["Misumi HFSB5-2020-" + x_frame_extrusion + "-TPW"] += 3;
    bom["Frame"]["Misumi HFSB5-2020-" + y_frame_extrusion + "-TPW"] += 4;
    // Bottom Rear Y frame
    bom["Frame"]["Misumi HFSB5-2020-" + x_frame_extrusion + "-AH" + (x_frame_extrusion / 2) + "-TPW"] = 1;

    // Trident Bed Frame
    bom["Frame"]["Misumi HFSB5-2020-" + (build_y - 18) + "-LTP"] = 1; // Magic number to get to 232 on a 250 build for rear bed extrusion
    bom["Frame"]["Misumi HFSB5-2020-" + x_frame_extrusion + "-AH" + (x_frame_extrusion / 2)] = 1;
    bom["Fasteners"]["M5x16 BHCS"] += 1;

    // Belts
    bom["Motion"]["GT2 Open Belt LL-2GT-6 (6mm wide) - " + ((frame_x + frame_y) * 2 + 50) + "mm"] = 2;

    // Enclosure Panels
    bom["Panels"] = {};
    // Deck + Bottom
    bom["Panels"]["Coroplast Sheet - " + (x_frame_extrusion - 1) + "x" + (y_frame_extrusion - 1) + "x4 mm"] = 2
        // Back
    bom["Panels"]["Coroplast Sheet - " + (frame_x - 28) + "x" + (frame_z - 28) + "x4 mm"] = 1

    // Doors
    bom["Panels"]["Acrylic Sheet Clear - " + ((frame_x - 27) / 2) + "x" + (frame_z - 27) + "x3 mm"] = 0
    bom["Panels"]["Acrylic Sheet Clear - " + ((frame_x - 27) / 2) + "x" + (frame_z - 27) + "x3 mm"] += 2
        // Sides
    bom["Panels"]["Acrylic Sheet Clear - " + (frame_y - 27) + "x" + (frame_z - 27) + "x3 mm"] = 0
    bom["Panels"]["Acrylic Sheet Clear - " + (frame_y - 27) + "x" + (frame_z - 27) + "x3 mm"] += 2
        // Top
    bom["Panels"]["Acrylic Sheet Clear - " + (frame_x - 27) + "x" + (frame_y - 27) + "x3 mm"] = 0
    bom["Panels"]["Acrylic Sheet Clear - " + (frame_x - 27) + "x" + (frame_y - 27) + "x3 mm"] += 1

    // Build Plate
    bom["Buildplate"] = {}
    bom["Buildplate"]["3M 468MP Adhesive Sheet - " + convert_to_inch(build_x) + "\"x" + convert_to_inch(build_y) + "\""] = 1;
    bom["Buildplate"]["PEI 0.04\" Sheet - " + convert_to_inch(build_x) + "\"x" + convert_to_inch(build_y) + "\""] = 1;
    bom["Buildplate"]["MIC6 5/16\" Plate - " + convert_to_inch(build_x) + "\"x" + convert_to_inch(build_y) + "\""] = 1;
    bom["Buildplate"]["Keenovo Silicone AC Heater w/ thermistor - " + (build_x - 50) + "x" + (build_y - 50) + "mm (" + get_heater_wattage(build_x, build_y) + "W)"] = 1;
}
