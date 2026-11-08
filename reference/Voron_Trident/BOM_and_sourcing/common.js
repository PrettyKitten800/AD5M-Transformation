let sourcing_gid = {
    "None": "",
    "V0": "1015161064",
    "V1.8": "2038895625",
    "V2.4": "1297316004",
    "VS": "675050663",
    "Mobius": "673174242",
    "M4": "226615058",
    "VT": "414191639",
    "VSB": "1229582267",
    "Cascade": "1010395226"
}

let sourcing_guide_url = `https://docs.google.com/spreadsheets/d/e/2PACX-1vS_jv9UtoSkgQoYD47VE9wIpTnjsEbzAREPG8895b6UL0v99OIfVEJQ4BHl2w_Rn6V0YUe1ldfPjone/pubhtml?widget=false&headers=false&gid=${sourcing_gid[model_name]}`

$(document).ready(function() {
    $("#sourcing-guide-embed").attr("src", sourcing_guide_url);
});

function generate_bom_csv() {
    var csv = 'Category;Description;Qty;Notes\n';
    $.each(bom, function(category, parts) {
        var new_category = true;
        $.each(parts, function(item, count) {
            if (new_category) {
                csv += category + ";" + item + ";" + count + ";\n";
                new_category = false;
            } else {
                csv += ";" + item + ";" + count + ";\n";
            }
        });
    });
    const blob = new Blob(
        [csv], { type: 'text/csv' }
    );
    const url = URL.createObjectURL(blob);

    return url;
}

function generate_bom_table() {
    var html = "<table class='table table-sm'>";
    html += "<tr><td><h4>Bill of Materials</h4></td><td></td><td></td></tr>"
    html += "<tr class='table-dark'><td><b>Category:</b></td><td><b>Part Description:</b></td><td><b>Qty:</b></td></tr>";
    $.each(bom, function(category, parts) {
        var note = "";
        if (category == "Fasteners") {
            note = "Listed quantities are minimum, buy extra!";
        }
        var new_category = true;
        var part_desc = Object.keys(parts).sort().reverse();
        $.each(part_desc, function(index, part) {
            if (new_category) {
                html += "<tr class='table-active'><td>" + category + "</td><td>" + note + "</td><td></td></tr>";
                new_category = false;
            }
            html += "<tr><td></td><td>" + part + "</td><td>" + parts[part] + "</td></tr>";
        });
    });

    html += "</table>";

    return html;
}

function get_heater_wattage(build_x, build_y) {
    var raw_watts = Math.round(0.0055 * (build_x * build_y));
    var heater_specs = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750];
    var heater_value = 750;
    $.each(heater_specs, function(index, value) {
        const rem = value - raw_watts;
        if (rem > -50) {
            heater_value = value;
            return false;
        }
    });
    return heater_value;
}

function get_screws_per_rail(rail_length) {
    return Math.round(rail_length / 40) + 1;
}

function convert_to_inch(mm) {
    return Math.round(mm * 0.03937007874);
}

function convert_to_ft(mm) {
    mm = mm * 0.00328084
    return Math.round((mm + Number.EPSILON) * 100) / 100
}

function calculate_zipchain_links(type, length) {
    if (type == "z") {
        return Math.round(length / 40);
    } else {
        return Math.round(length / 33.489);
    }
}
