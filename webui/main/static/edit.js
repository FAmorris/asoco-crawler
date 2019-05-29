function isUntitleFile(filename) {
    return filename == null || filename.startsWith("untitle") || filename == ""
}

function loadConfigJson(filename, callback) {
    if (isUntitleFile(filename)) {
        $.getJSON("/static/default-config.json", function (resp) {
            callback(resp)
        })
    } else {
        $.getJSON("/readContent", {
            filename: filename
        }, function (resp) {
            callback(resp)
        })
    }
}


function showMsgModal(msg) {
    if (msg != null && msg.length > 0) {
        $("#msgModal .modal-body").text(msg)
        $("#msgModal").modal()
    }
}

function saveJSON(global, nowfilename, nowData) {
    if (isUntitleFile(nowfilename)) {
        showMsgModal("请输入文件名")
        return
    }
    if (nowfilename.endsWith(".json") == false) {
        nowfilename += ".json"
    }
    $.post("/savefile", {
        oldFilename: global.filename,
        filename: nowfilename,
        content: nowData
    }, function (resp) {
        if (resp == 'ok') {
            global.originalData = nowData
            global.filename = nowfilename//更新旧文件名
            showMsgModal("保存成功！")
            setTimeout(function () {
                $("#msgModal").modal("hide")
            }, 1000)
        } else {
            showMsgModal(resp)
        }
    })

}