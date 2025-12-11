$(function () {

    /* Functions */

    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-announcement .modal-content").html("");
                $("#modal-announcement").modal("show");
            },
            success: function (data) {
                $("#modal-announcement .modal-content").html(data.html_form);
            }
        });
    };

    var saveForm = function () {
        var form = $(this);
        // Use FormData to handle file uploads
        var formData = new FormData(form[0]);
        $.ajax({
            url: form.attr("action"),
            data: formData,
            type: form.attr("method"),
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function (data) {
                if (data.form_is_valid) {
                    if (data.html_announcement_list) {
                        // We are updating an item in the list
                        // Find the existing item card and replace it? 
                        // Actually, the button is inside the card.
                        // We need to identify the card properly.
                        // Simplest way: reload page OR safer: replace the content relative to the button that opened it?
                        // BUT: the button ID is lost after modal open.

                        // We can't easily find the item without an ID on the card col.
                        // Let's reload for simplicity or find by ID if we could.
                        // Wait, I updated views.py to return 'html_announcement_list' which is the ITEM partial.
                        // I should add an ID to the col in the partial. 
                        location.reload();
                    } else {
                        // Deletion success
                        location.reload();
                    }
                    $("#modal-announcement").modal("hide");
                } else {
                    $("#modal-announcement .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };


    /* Binding */

    // Update Announcement
    $("#announcement-list").on("click", ".js-update-announcement", loadForm);
    $("#modal-announcement").on("submit", ".js-announcement-update-form", saveForm);

    // Delete Announcement
    $("#announcement-list").on("click", ".js-delete-announcement", loadForm);
    $("#modal-announcement").on("submit", ".js-announcement-delete-form", saveForm);

});
