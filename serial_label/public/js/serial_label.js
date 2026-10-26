frappe.listview_settings["Serial No"] = frappe.listview_settings["Serial No"] || {};

const _serial_label_onload = frappe.listview_settings["Serial No"].onload;

frappe.listview_settings["Serial No"].onload = function (listview) {
  if (_serial_label_onload) _serial_label_onload(listview);

  listview.page.add_action_item(__("Print Label 3 Kolom"), () => {
    const names = listview.get_checked_items().map((d) => d.name);
    if (!names.length) {
      return frappe.msgprint(__("Pilih serial no terlebih dahulu"));
    }
    window.open(
      "/api/method/serial_label.serial_label.print_serial_labels?names=" +
        encodeURIComponent(JSON.stringify(names))
    );
  });
};
