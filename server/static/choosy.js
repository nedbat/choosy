/* Javascript for choosepython.com */
var choosy = {

    // set_csrf_token: store the CSRF token for later.
    set_csrf_token: function(csrf_token) {
        choosy.csrf_token = csrf_token;
    },

    // run_python: run student's code, get the results, and display them.
    run_python: function(exid, code, stdout, checks) {
        // Clear the output areas.
        $(stdout).val("");
        $(checks).html("");

        // Figure out where we're going to post to.
        var url = "/gym/run/";
        if (exid) {
            url += exid + "/";
        }

        // The ajax call!
        $.ajax({
            type: "POST",
            dataType: "json",
            url: url,
            data: {
                code: $(code).val(),
                csrfmiddlewaretoken: choosy.csrf_token,
            },
            success: function(obj) {
                // Show or hide the stdout container.
                if (obj.stdout) {
                    $(stdout).show();
                }
                else {
                    $(stdout).hide();
                }
                $(stdout).val(obj.stdout);

                // Write the results into the results container.
                $(obj.checks).each( function(i, res) {
                    if (res.status === "ERROR") {
                        $(checks).append($("<pre class='ERROR'>").text(res.did));
                    }
                    else {
                        var p = $("<p class='" + res.status + "'>").text(res.expect);
                        $(checks).append(p)
                        if (res.did) {
                            p.append($("<span class='did'>").text(res.did));
                        }
                    }
                });
            }
        });
    },

    // make_html_editor: turn textareas into TinyMCE html editors.
    make_html_editor: function(id) {
        tinyMCE.init({
            theme: "advanced",
            mode: "exact",
            elements: id,
            content_css: "/static/style.css",
            theme_advanced_toolbar_location: "top",
            theme_advanced_buttons1: "cut,copy,paste,|,"
                + "bold,italic,underline,|,"
                + "bullist,numlist,"
                + "link,unlink,|,"
                + "undo,redo,cleanup,code,charmap",
            theme_advanced_buttons2: "",
            theme_advanced_buttons3: "",
            height:"350px",
            width:"100%"
        });
    },

    // make_py_editor: turn textareas into CodeMirror text editors.
    make_py_editor: function(elts) {
        return CodeMirror.fromTextArea(elts[0], {
            mode: {
                name: "python",
                version: 2,
                singleLineStringErrors: true
                },
            theme: "eclipse",
            lineNumbers: true,
            tabMode: "shift",
            indentUnit: 4
            });
    }
};
