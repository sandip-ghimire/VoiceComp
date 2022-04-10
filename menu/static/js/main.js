var audio;
var audio1;
var audio2;

//Hide Pause Initially
$('#pause1').hide();
$('#buffer1').hide();
$('#pause2').hide();
$('#buffer2').hide();

//Initializer
audio1 = $('#playlist1 li:first-child');
initAudio(audio1, 'player1');

audio2 = $('#playlist2 li:first-child');
initAudio(audio2, 'player2');

function initAudio(element, player) {
	var song = element.attr('song');
	var title = element.text();
	var artist = element.attr('artist');

	//Create a New Audio Object
    audio = new Audio('/audio/voicedata/wav/' + song);


	if (!audio.currentTime) {
		$('.duration').html('0.00');
	}

	if (player == 'player1') {
		$('#audio-player1 .title').text(title);

	} else {
		$('#audio-player2 .title').text(title);

	}

}

//Play Button
$('#play1').click(function () {
	if (audio.paused) {
		var curtime = $('#progress1').attr('curtime');
		if (typeof curtime !== typeof undefined && curtime !== false) {
			initAudio(audio1, 'player1');
			audio.currentTime = parseFloat(curtime);
			audio.play();
			$('#play1').hide();
			$('#buffer1').hide();
			$('#pause1').show();
			$('#duration1').fadeIn(400);
			showDuration(1);
			return;
		}
	} else {
		if (audio.duration > 0) {
			$('#pause2').trigger('click');
		}
	}
	initAudio(audio1, 'player1');
	audio.play();
	audio.addEventListener("loadstart", function () {
		$('#play1').hide();
		$('#pause1').hide();
		$('#buffer1').show();
	});
	audio.addEventListener("loadedmetadata", function () {
		$('#play1').hide();
		$('#buffer1').hide();
		$('#pause1').show();
	});

	$('#duration1').fadeIn(400);
	showDuration(1);
});

$('#play2').click(function () {
	if (audio.paused) {
		var curtime = $('#progress2').attr('curtime');
		if (typeof curtime !== typeof undefined && curtime !== false) {
			initAudio(audio2, 'player2');
			audio.currentTime = parseFloat(curtime);
			audio.play();
			$('#play2').hide();
			$('#buffer2').hide();
			$('#pause2').show();
			$('#duration2').fadeIn(400);
			showDuration(2);
			return;
		}
	} else {
		if (audio.duration > 0) {
			$('#pause1').trigger('click');
		}
	}
	// audio2 = $('#playlist2 li');
	initAudio(audio2, 'player2');
	audio.play();
	audio.addEventListener("loadstart", function () {
		$('#play2').hide();
		$('#pause2').hide();
		$('#buffer2').show();
	});
	audio.addEventListener("loadedmetadata", function () {
		$('#play2').hide();
		$('#buffer2').hide();
		$('#pause2').show();
	});

	$('#duration2').fadeIn(400);
	showDuration(2);
});

//Pause Button
$('#pause1').click(function () {
	audio.pause();
	$('#progress1').attr('curtime', audio.currentTime);
	$('#pause1').hide();
	$('#play1').show();
});

$('#pause2').click(function () {
	audio.pause();
	$('#progress2').attr('curtime', audio.currentTime);
	$('#pause2').hide();
	$('#play2').show();
});


$('#multiplecheck').on('change', function (e) {
	if ($(this).prop('checked')) {

		$('#multiplecheck').attr('ismultiple','true');
		$('.optionsblock').slideDown(300);
	} else {
		$('#multiplecheck').attr('ismultiple','false');
		$('.optionsblock').slideUp(300);
	}
})

$('#consentCheckBox').on('change', function (e) {
    if (this.checked){
        $('.submitinfo').prop('disabled', false);
    }else{
        $('.submitinfo').prop('disabled', true);
    }
})


$('.lighttheme').on('click', function (e) {
	$.ajax({
		url: URL + "themechange",
		type: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: {
			theme: 'light',
		},
		success:function(response){
			location.reload();
		}
	})

})

$('.darktheme').on('click', function (e) {
	$.ajax({
		url: URL + "themechange",
		type: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: {
			theme: 'dark',
		},
		success:function(response){
			location.reload();
		}
	})

})


//Time Duration
function showDuration(player) {
	$(audio).bind('timeupdate', function () {
		//Get hours and minutes
		var s = parseInt(audio.currentTime % 60);
		var m = parseInt((audio.currentTime / 60) % 60);
		//Add 0 if seconds less than 10
		if (s < 10) {
			s = '0' + s;
		}

		var value = 0;
		if (audio.currentTime > 0) {
			value = Math.floor((100 / audio.duration) * audio.currentTime);
		}

		if (player == 1) {
			$('#duration1').html(m + '.' + s);
			$('#progress1').css('width', value + '%');
			if (audio.duration == audio.currentTime) {
				$('#duration1').html('0.00');
				$('#pause1').hide();
				$('#play1').show();
				$('#progress1').removeAttr('curtime');

			}
		}

		else if (player == 2) {
			$('#duration2').html(m + '.' + s);
			$('#progress2').css('width', value + '%');
			if (audio.duration == audio.currentTime) {
				$('#duration2').html('0.00');
				$('#pause2').hide();
				$('#play2').show();
				$('#progress2').removeAttr('curtime');

			}
		}
	});
}

$('.loginbtn').click(function () {
	var username = $.trim($('#uname').val());
	var pwd = $.trim($('#pass').val());

	$.ajax({
		url: URL + "login",
		type: "POST",
		// contentType: 'application/json',
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: {
			username: username,
			password: pwd,
		}
	}).done(function (data) {
		if (data == "success") {
			$('#loginModal').modal('toggle');
			location.reload();
		} else {
			$('.loginfailed').css('display', 'block');
		}
	});
});

$('.saveSettings').click(function () {
	$('.errordiv').css('display', 'none');
	var multiplecheck = $('#multiplecheck').prop('checked');
	var choicestxt = $('#choices-list-item').val();
	var instructiontxt = $('#instruction-txt').val();
	var samepoint = $('.samepoint').val();
	var differentpoint = $('.differentpoint').val();
	var set = $('.setting-btn').attr('selectedval');

	var tempdata = localStorage.getItem('temp');
	if (!tempdata && (choicestxt || samepoint || differentpoint)) {
		$('.errortxt').text("Please add option to the list and then save");
		$('.errordiv').css('display', 'block');
		$("#settingModal").scrollTop(1000);
		return;
	}

	// if ($('.uploadImage')[0].files.length > 0) {
		if (!$.isEmptyObject(uploadfile)) {
		var file = uploadfile;
		var fileType = file["type"];
		var validImageTypes = ["image/gif", "image/jpeg", "image/png"];

		if ($.inArray(fileType, validImageTypes) > -1) {
			sendSettingData(file, multiplecheck, choicestxt, instructiontxt, samepoint, differentpoint, set, tempdata);
		}
	} else {
		if ($('.imgPreview').css('background-image') != 'none') {
			var url = validateFile($('.imgPreview').css('background-image').replace(/^url\(['"](.+)['"]\)/, '$1'));
			if (url) {
				$.when(convertToFile(url)).done(function (file) {
					sendSettingData(file, multiplecheck, choicestxt, instructiontxt, samepoint, differentpoint, set, tempdata);
				});
			} else {
				sendSettingData('' , multiplecheck, choicestxt, instructiontxt, samepoint, differentpoint, set, tempdata);
			}
		}
	}


});

function sendSettingData(file, multiplecheck, choicestxt, instructiontxt, samepoint, differentpoint, set, tempdata) {
	var fd = new FormData();
	var setval = $('.setting-btn').attr('set');
	if (file) {
		fd.append('image', file);
	}
	if (setval) {
		fd.append('setval', setval);
	}

	if (validAudioList) {
		if ($('.uploadAudioList')[0].files.length > 0) {
			var file = $('.uploadAudioList')[0].files[0];
			fd.append('audiolist', file);
		}
	}

	if (validScoreFile) {
		if ($('.uploadAudioScore')[0].files.length > 0) {
			var file = $('.uploadAudioScore')[0].files[0];
			fd.append('audioscore', file);
		}
	}

	var togglevalue = $('#randomizeToggle').prop('checked');
	var shufflevalue = $('#shuffleToggle').prop('checked');
	if (togglevalue){
	    var randomization = 'randomize';
	}else{
	    var randomization = (shufflevalue) ? 'shuffle' : 'sequential';
	}
	//var randomization = (togglevalue) ? 'randomize' : 'sequential';
	var addop = (tempdata) ? tempdata : '';
	fd.append('randomization', randomization);

	fd.append('multiplecheckbox', multiplecheck);
	fd.append('choicestxt', choicestxt);
	fd.append('instructiontxt', instructiontxt);
	fd.append('samepoint', samepoint);
	fd.append('differentpoint', differentpoint);
	fd.append('set', set);
	fd.append('addop', addop)
	localStorage.removeItem('temp');
	$('.loader').show();
	$.ajax({
		url: URL + "settings",
		type: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: fd,
		contentType: false,
		processData: false,
	}).done(function (data) {
		$('.loader').hide();
		if (Object.keys(data)[0] == "success") {
			location.reload();
		} else if (Object.keys(data)[0] == "error"){
			$('.errortxt').text(data.error);
			$('.errordiv').css('display', 'block');
			$("#settingModal").scrollTop(1000);
		}
	}).fail(function (data) {
		$('.loader').hide();
		console.log(data);
	});
}

$('.opennewsetting').click(function () {
	$('#settingModal').removeClass('fade');
	$('#settingModal').modal('hide');
	$('#settingnameModal').modal('show');
	$('#setsettingname').val('');

});

$('#settingnameModal').on('shown.bs.modal', function (e) {
	$('.settingerrdiv').css('display', 'none');
	// $('#settingModal').removeClass('fade');
	// $('#settingModal').modal('hide');
})

$('#settingnameModal').on('hidden.bs.modal', function (e) {
	$('#settingModal').modal('show');
	$('#settingModal').addClass('fade');
})

$('.setsettingbtn').on('click', function () {
	var settingname = $('#setsettingname').val();
	var oldname = $('.setting-btn').attr('selectedval');
	var listset = localStorage.getItem('setlist');
	var settingNameErrTxt = $('.settingerr');
	var settingNameErrDiv = $('.settingerrdiv');

	$('.errordiv').css('display', 'none');
	$.when(checkName(listset, settingname, settingNameErrTxt, settingNameErrDiv)).done(function () {
		$('.setting-btn').text(settingname);
		$('.setting-btn').attr('selectedval', settingname);
		$('.setting-btn').attr('newset', settingname);
		if (oldname) {
			$('.settingdropdownoptions').append("<a class='dropdown-item othersettings' href='#'>" + oldname + "</a>")
		}
		$('#settingnameModal').modal('toggle');
		$('#list-items').empty();
	 });
});

$('.btn-exit').click(function () {

    $.ajax({
		url: URL + "generatetoken",
		type: "POST",
		tryCount: 0,
        retryLimit: 10,
        tryCount2: 0,
        retryLimit2: 3,
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		success:function(response){
		    $('#uniquetoken').val(response.token);
		    $('#totalhits').val(response.hits);
			$('#exitModal').modal('show');
		},
		error: function(xhr, txtStatus, errorThrown){
            if (txtStatus == 'error' && xhr.status == 0){
                this.tryCount++;
                if (this.tryCount <= this.retryLimit){
                    $.ajax(this);
                    return;
                }
            } else {
                this.tryCount2++;
                if (this.tryCount2 <= this.retryLimit2){
                    $.ajax(this);
                    return;
                }
            }
        }
	});

});

$('.copybtn').click(function () {
    $('#uniquetoken').select();
	document.execCommand("copy");
});

$('.copyexittoken').click(function () {
    $('#exitToken').select();
	document.execCommand("copy");
});

$('#randomizeToggle').change(function() {
    var togglevalue = $('#randomizeToggle').prop('checked');
    if (togglevalue){
        $('#shuffleToggle').prop('checked', false);
        $('#shuffleToggle').prop('disabled', true);

    }else{
        $('#shuffleToggle').prop('disabled', false);
    }
});

$('.checkvalidity').on('click', function () {
    var workerToken =  $('#wtoken').val();
    var workerId =  $('#mturkwid').val();

    if (workerToken || workerId){
        $.ajax({
            url: URL + "getdatabytoken",
            type: "POST",
            data: {
                workertoken: workerToken,
                workerid: workerId
            },
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            success:function(data){
                 if (data && Object.keys(data)[0] != "error") {
                    var tscore = data.tscore || '';
                    var ttime = data.ttime || '';
                    var mtwid = data.mtwid || '';
                    var thits = data.tcount || '';

                    var wscore = data.wscore || '';
                    var wtime = data.wtime || '';
                    var whits = data.wcount || '';

                    $('#storedwid').val(mtwid);
                    $('#wscore').val(tscore);
                    $('#timespent').val(ttime);
                    $('#ttotaltrials').val(thits);

                    $('#scorebywid').val(wscore);
                    $('#timespentbywid').val(wtime);
                    $('#wtotaltrials').val(whits);

                    if (mtwid == workerId) {
                        $('.verifyworker').css('display', 'block');
                    }else{
                        $('.verifyworker').css('display', 'none');
                    }


                 }else{
                    $('.mtverifyerr').text(data.error);
				    $('.mtverifyerrdiv').css('display', 'block');
                 }
            }
        });
    }
});

$('.clearbtn').on('click', function () {
    $('#wtoken').val('');
    $('#mturkwid').val('');

    $('#storedwid').val('');
    $('#wscore').val('');
    $('#timespent').val('');
    $('#ttotaltrials').val('');

    $('#scorebywid').val('');
    $('#timespentbywid').val('');
    $('#wtotaltrials').val('');

    $('.mtverifyerr').text('');
    $('.mtverifyerrdiv').css('display', 'none');

    $('.verifyworker').css('display', 'none');

});

function checkName(namelist, name, errtxt, errdiv) {
	var list = namelist.split(',');
	var d = $.Deferred();
	$.each(list, function (i, item) {
		if ($.trim(item.toLowerCase()) === $.trim(name.toLowerCase())) {
			errtxt.text("Setting name already exists!");
			errdiv.css('display', 'block');
			d.reject();
			return false;
		}
	});
	d.resolve();
	return d.promise();
}

function validateFile(url) {
	var validurl = '';
	var validExt = ["gif", "jpg", "jpeg", "png"];
	var fileName = url.split('/').pop();
	var ext = fileName.split('.').pop();
	if ($.inArray(ext, validExt) > -1) {
		validurl = url;
	}
	return validurl;
}

function convertToFile(url) {
	var blob = null;
	var file = null;
	var fileName = url.split('/').pop();
	var d = $.Deferred();
	var xhr = new XMLHttpRequest();
	xhr.open("GET", url, true)
	xhr.responseType = "blob"
	xhr.send()
	xhr.onload = function()
	{
		blob = xhr.response;
		file = new File([blob], fileName);
		d.resolve(file);

	}
	return d.promise();
}

$("body").on("click", ".othersettings", function () {
	var setname = $(this).text();
	var oldname = $('.setting-btn').attr('selectedval');
	var store = JSON.parse(localStorage.getItem(setname));

	$('#list-items').empty();
	$('#list-items').html(store.table);
	$('#instruction-txt').text(store.ins[0].text);
	$('.imgPreview').css("background-image", "url(" + store.ins[0].url + ")");
	if (store.ins[0].url) {
		$('.imgicn').hide();
	} else {
		$('.imgicn').show();
	}

	$('.setting-btn').text(setname);
	$('.setting-btn').attr('selectedval', setname);
	$('.setting-btn').attr('set', store.set);

	if (store.rand === 'sequential') {
		$('#randomizeToggle').bootstrapToggle('off');
	} else if (store.rand === 'randomize') {
		$('#randomizeToggle').bootstrapToggle('on');
	} else if (store.rand === 'shuffle') {
	    $('#randomizeToggle').bootstrapToggle('off');
	    $('#shuffleToggle').prop('checked', true);
	}

	if ($('.uploadAudioList')[0].files.length > 0) {
		var file = $('.uploadAudioList')[0].files[0];
		$('#list-txt').text(file.name);
	} else {
		$('#list-txt').text(store.aud.split('/')[1]);
	}

	if ($('.uploadAudioScore')[0].files.length > 0) {
		var file = $('.uploadAudioScore')[0].files[0];
		$('#score-txt').text(file.name);
	} else {
		$('#score-txt').text(store.sco.split('/')[1]);
	}


	$(".othersettings").filter(function () {
		return $(this).text() === setname;
	}).remove();


	if (oldname) {
		$('.settingdropdownoptions').prepend("<a class='dropdown-item othersettings' href='#'>" + oldname + "</a>")
	}

});

$(document).on("change", ".uploadImage", function () {
	if (this.files) {
		var file = this.files[0];
		var fileType = file["type"];
		var validImageTypes = ["image/gif", "image/jpeg", "image/png"];

		if ($.inArray(fileType, validImageTypes) > -1) {
			uploadfile = file;
			var reader = new FileReader();
			reader.readAsDataURL(file);

			reader.onloadend = function (e) {
				$('.imgPreview').css("background-image", "url(" + e.target.result + ")");
				$('.imgicn').hide();
			}
		}
	}

});

$(document).on("change", ".uploadAudioList", function () {
	$('.errordiv').css('display', 'none');
	if (this.files) {
		var file = this.files[0];
		if (file) {
			var fileType = file["type"];
			var validFileTypes = ["text/plain"];

			if ($.inArray(fileType, validFileTypes) > -1) {
				$('#list-txt').text(file.name);
				validAudioList = true;
			} else {
				validAudioList = false;
				$('#list-txt').text('No file');
				$('.errortxt').text('Invalid file type. Please upload .txt file');
				$('.errordiv').css('display', 'block');
				$("#settingModal").scrollTop(1000);
			}
		}

	}

});

$(document).on("change", ".uploadAudioScore", function () {
	$('.errordiv').css('display', 'none');
	if (this.files) {
		var file = this.files[0];
		if (file) {
			var fileName = file["name"];
			var ext = fileName.split('.').pop();

			if (ext === 'npy') {
				$('#score-txt').text(fileName);
				validScoreFile = true;
			} else {
				validScoreFile = false;
				$('#score-txt').text('No file');
				$('.errortxt').text('Invalid file type. Please upload .npy file');
				$('.errordiv').css('display', 'block');
				$("#settingModal").scrollTop(1000);
			}
		}

	}

});

$('.dltImage').click(function () {
	$('.imgPreview').css("background-image", "url('')");
	uploadfile = {};
	$('.imgicn').show();

});

$('.rename-set').click(function () {
	$('.setting-btn').removeClass('dropdown-toggle');
	$('.setting-btn').prop('contenteditable', true);
	$('.setting-btn').removeAttr('data-toggle');
	$('.setting-btn').focus();
	$('.setting-btn').css('cursor', 'initial');
	$(this).hide();
	$('.add-set').hide();
	$('.downloadreport').hide();
	$('.done-rename').show();
	$('.cancel-rename').show();
	$(".settingdropdown .dropdown-menu").hide();
});

$('.cancel-rename').click(function () {

	revertEditMode();
	$('.setting-btn').text($('.setting-btn').attr('selectedval'));

});

$('.done-rename').click(function () {

	var newname = $('.setting-btn').text();
	var oldname = $('.setting-btn').attr('selectedval');
	var listset = localStorage.getItem('setlist');
	var settingModalErrTxt = $('.errortxt');
	var settingModalErrDiv = $('.errordiv');

	$('.errordiv').css('display', 'none');

	if (!newname) {
		settingModalErrTxt.text('Setting name not valid!');
		settingModalErrDiv.css('display', 'block');
		$("#settingModal").scrollTop(1000);
		return;
	}

	$.when(checkName(listset, newname, settingModalErrTxt, settingModalErrDiv)).done(function () {

		$.ajax({
			url: URL + "renamesetting",
			type: "POST",
			headers: { "X-CSRFToken": getCookie("csrftoken") },
			data: {
				newname: newname,
				oldname: oldname,
			}
		}).done(function (data) {
			if (Object.keys(data)[0] == "success") {
				revertEditMode();
				$('.setting-btn').text(data.success);

			} else if (Object.keys(data)[0] == "error"){
				$('.errortxt').text(data.error);
				$('.errordiv').css('display', 'block');
				$("#settingModal").scrollTop(1000);
			}
		}).fail(function (data) {
			console.log("Server Error");
		});

	});

	revertEditMode();
	$('.setting-btn').text($('.setting-btn').attr('selectedval'));

});

function revertEditMode() {
	$('.setting-btn').addClass('dropdown-toggle');
	$('.setting-btn').prop('contenteditable', false);
	$('.setting-btn').attr('data-toggle', 'dropdown');
	$('.setting-btn').css('cursor', 'pointer');
	$('.rename-set').show();
	$('.add-set').show();
	$('.downloadreport').show();
	$('.done-rename').hide();
	$('.cancel-rename').hide();
	$(".settingdropdown .dropdown-menu").removeAttr('style');

}

$('.downloadreport').click(function () {
	var setting = $('.setting-btn').text();

	window.location = URL + "downloadreport?setting=" + setting;


});

$('.continuebtn').click(function () {
	location.reload();
	$('#levelsuccessModal').modal('hide');
});

$('.retrybtn').click(function () {
	location.reload();
	$('#levelfailModal').modal('hide');
});

$('.resetgame').click(function () {
	resetgame();
});

$('.restartbtn').click(function () {
	resetgame();
});


$('.submitfeedback').click(function () {
	var rating = $.trim($('#feedrating').val());
	var likefeed = $.trim($('#feedlike').val());
	var dislikefeed = $.trim($('#feeddislike').val());

	$.ajax({
		url: URL + "feedback",
		type: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: {
			rating: rating,
			likefeed: likefeed,
			dislikefeed: dislikefeed,
		}
	}).done(function (data) {
		if (data == "success") {
			$('#feedbackModal').modal('hide');
		} else {
			console.log('Error saving feedback');
		}
	});

});

$('.submitinfo').click(function () {
	var infoexp = $.trim($('#infoexperience').val());
	var infolang = $.trim($('#infolanguage').val());
	var infodisability = $.trim($('#infodisability').val());
	var infospeaker = $.trim($('#infospeaker').val());
	var infobackground = $.trim($('#infobackground').val());
	var infodevice = $.trim($('#infodevice').val());

	$.ajax({
		url: URL + "playerinfo",
		type: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		data: {
			infoexp: infoexp,
			infolang: infolang,
			infodisability: infodisability,
			infospeaker: infospeaker,
			infobackground: infobackground,
			infodevice: infodevice
		}
	}).done(function (data) {
		if (data == "success") {
			$('#infodataModal').modal('hide');
			localStorage.setItem('infochecked','true');
		} else {
			console.log("Error saving participant's info");
		}
	});

});

function resetgame() {
    lv_store = startlv;
	score = 0;
	counter = 1;
	localStorage.setItem('score',score);
	localStorage.setItem('counter', counter);
	localStorage.setItem('prevscore', score);
	document.cookie = 'index' + "=" +  counter + "; path=/";
	//document.cookie = 'cslevel' + "=" +  lv_store + "; path=/";
	document.cookie = "seq=0; path=/";
	$('.level').text(lv_store);
	$('.scoretxt').text(score);
	$('.countertxt').text('#' + counter);
	$.ajax({
        url: URL + "resetgame",
        type: "POST",
        tryCount: 0,
        retryLimit: 10,
        tryCount2: 0,
        retryLimit2: 3,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        success:function(data){
             if (data == "success") {
                location.reload();
             }
        },
        error: function(xhr, txtStatus, errorThrown){
            if (txtStatus == 'error' && xhr.status == 0){
                this.tryCount++;
                if (this.tryCount <= this.retryLimit){
                    $.ajax(this);
                    return;
                }
            } else {
                this.tryCount2++;
                if (this.tryCount2 <= this.retryLimit2){
                    $.ajax(this);
                    return;
                }
            }
        }
    })

}

function setScore(score) {
    $.ajax({
        url: URL + "setscore",
        type: "POST",
        data: {
			score: score,
		},
        tryCount: 0,
        retryLimit: 10,
        tryCount2: 0,
        retryLimit2: 3,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        success:function(data){
             if (data == "success") {
                return data;
             }
        },
        error: function(xhr, txtStatus, errorThrown){
            if (txtStatus == 'error' && xhr.status == 0){
                this.tryCount++;
                if (this.tryCount <= this.retryLimit){
                    $.ajax(this);
                    return;
                }
            } else {
                this.tryCount2++;
                if (this.tryCount2 <= this.retryLimit2){
                    $.ajax(this);
                    return;
                }
            }
        }
    });

}

function setLevel(level) {
    $.ajax({
        url: URL + "setlevel",
        type: "POST",
        data: {
			level: level,
		},
        tryCount: 0,
        retryLimit: 10,
        tryCount2: 0,
        retryLimit2: 3,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        success:function(data){
             if (data == "success") {
                return data;
             }
        },
        error: function(xhr, txtStatus, errorThrown){
            if (txtStatus == 'error' && xhr.status == 0){
                this.tryCount++;
                if (this.tryCount <= this.retryLimit){
                    $.ajax(this);
                    return;
                }
            } else {
                this.tryCount2++;
                if (this.tryCount2 <= this.retryLimit2){
                    $.ajax(this);
                    return;
                }
            }
        }
    });

}

function addRating(field, txt, value) {
    $.ajax({
        url: URL + "setrating",
        type: "POST",
        data: {
			field: field,
			txt: txt,
			value: value
		},
        tryCount: 0,
        retryLimit: 10,
        tryCount2: 0,
        retryLimit2: 3,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        success:function(data){
             if (data == "success") {
                return data;
             }
        },
        error: function(xhr, txtStatus, errorThrown){
            if (txtStatus == 'error' && xhr.status == 0){
                this.tryCount++;
                if (this.tryCount <= this.retryLimit){
                    $.ajax(this);
                    return;
                }
            } else {
                this.tryCount2++;
                if (this.tryCount2 <= this.retryLimit2){
                    $.ajax(this);
                    return;
                }
            }
        }
    });

}

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function setTheme(theme) {
	var root = document.documentElement;
	var theme = JSON.parse(theme);
	root.style.setProperty("--background", theme.background);
	root.style.setProperty("--body-background", theme.body_background);
	root.style.setProperty("--button-background", theme.button_background);
	root.style.setProperty("--dark-background", theme.dark_background);
	root.style.setProperty( "--light-grey", theme.light_grey);
	root.style.setProperty("--hover-grey", theme.hover_grey);
	root.style.setProperty("--theme-color", theme.theme_color);
	root.style.setProperty("--progress-theme", theme.progress_theme);
	root.style.setProperty("--theme-color-light", theme.theme_color_light);
	root.style.setProperty("--font", theme.font);
	root.style.setProperty("--textbox-background", theme.textbox_background);
	root.style.setProperty("--triangle-back", theme.triangle_back);
	root.style.setProperty("--triangle-hover", theme.triangle_hover);
}

function resizeMiddle() {

	var progresswidth = $('.tracker').width() - $('.duration').width() - 25;
	$('.progressBar').css({ "width": progresswidth });
}

switch (document.readyState) {
	case "loading":
		$('.loader2').fadeIn(1000);
		break;

	case "complete":
		$('.loader2').hide();
		break;
}


var interval = setInterval(function () {
	switch (document.readyState) {
		case "loading":
			$('.loader2').fadeIn(1000);
			break;


		case "complete":
			$('.loader2').hide();
			clearInterval(interval);
			break;
	}
}, 100);

$(document).ready(function () {

	resizeMiddle();

	$('.leftblock').animate({"left":"0"});
	$('.rightblock').animate({"right":"0"});

	$("#confslider").val(0);
	$("#confidencescore").val(0);
	$('.btnnext').prop('disabled', true);

	$(".addlisttxt").attr("autocomplete", "off");
	$(".txtbox").attr("autocomplete", "off");

	var maxlevel = maxlv;
	var prevscoreitem = localStorage.getItem('prevscore');
	var prevscore = (prevscoreitem) ? parseFloat(prevscoreitem) : 0;
	if (counter == 1) {
		prevscore = score;
		localStorage.setItem('prevscore',prevscore);
	}

	if (!isGamified){
	    $('.levelwrap').css({ "padding-bottom": "35px" });
	    if (counter > 10){
	        $('.btn-exit').removeClass('disabled');
	    }else {
	        $('.btn-exit').addClass('disabled');

	    }
	    $('.choicesradiobtns').find('input').prop('checked', false);
	    $('.gameovertitle').text('Survey Complete');
	    $('.exitgametitle').text('Exit Survey');

	} else {
	    if (lv_store > 1){
	        $('.btn-exit').removeClass('disabled');
	    }else {
	        $('.btn-exit').addClass('disabled');

	    }
	    $('.gameovertitle').text('Game Over!');
	    $('.exitgametitle').text('Exit Game');
	}

	if (isGamified){
        if (lv_store > 0 && lv_store <= maxlevel) {
            if (counter > totaltrials) {

                if (true) {
                    $('.completelv').text(lv_store);
                    counter = 1;
                    localStorage.setItem('counter', counter);
                    document.cookie = 'index' + "=" +  counter + "; path=/";
                    localStorage.setItem('prevscore',score);

                    if (lv_store == maxlevel) {
                        $('.levelmsg').text('You have reached max level');
                        $('.continuebtn').text('Play Again');

                        $('#gameOverModal').modal('show');
				        document.cookie = "_flg=1; path=/";

                    }

                    if (lv_store < maxlevel) {
                        lv_store++;
                        setLevel(lv_store);
                        $('#levelsuccessModal').modal('show');
                    }


                } else {
                    $('#levelfailModal').modal('show');
                    counter = 1;
                    score = prevscore;
                    setScore(score);
                    seq = (lv_store - 1) * totaltrials * 2;
                    iseq = seq + 2;
                    localStorage.setItem('score', score);
                    localStorage.setItem('counter', counter);
                    document.cookie = 'index' + "=" +  counter + "; path=/";
                    document.cookie = 'seq' + "=" +  seq + "; path=/";
                    document.cookie = 'iseq' + "=" +  iseq + "; path=/";
                }

            }
        } else {
            resetgame();
        }
    }else{
        var maxtrials = maxlevel * totaltrials;
        if (counter > maxtrials) {
            $('#gameOverModal').modal('show');
		    document.cookie = "_flg=1; path=/";
        }
    }

	$('#confidencescore').focusout(function () {
		var confidencescore = parseInt($('#confidencescore').val());
		if (confidencescore > 100){
            $('#confidencescore').val(100)
		}
		if (confidencescore < 0){
            $('#confidencescore').val(0)
		}
	});

	$('.choicesradiobtns').on('click', function(){
	    inputbtn = $(this).children('input');
	    inputbtn.prop('checked',true);
	    selectedbtn = inputbtn;
        selectedchoice = $.trim(inputbtn.attr('choice'));
        selectedsp = parseFloat(inputbtn.attr('choicesp'));
        selecteddp = parseFloat(inputbtn.attr('choicedp'));
        if (parseInt($('#confidencescore').val()) > 0){
            $('.btnnext').prop('disabled', false);
        }
	});

	$('.txtbox').on('keypress', function (e) {
		if (e.keyCode == 13) {
			e.preventDefault();
			$('.loginbtn').click();
		}
	});

	$('.addlisttxt').on('keypress', function (e) {
		if (e.keyCode == 13) {
			e.preventDefault();
			$('.add').click();
		}
	});

	$('#setsettingname').on('keypress', function (e) {
		if (e.keyCode == 13) {
			e.preventDefault();
			$('.setsettingbtn').click();
		}
	});

	$('#wtoken').on('keypress', function (e) {
		if (e.keyCode == 13) {
			e.preventDefault();
			$('.checkvalidity').click();
		}
	});

	$('.innerbutton').hover(function () {
		$(this).parent().find('.triangle-left').delay(50).queue(function (next) {
			$(this).addClass("darkback-left");
			next();
		});

		$(this).parent().find('.triangle-right').delay(50).queue(function (next) {
			$(this).addClass("darkback-right");
			next();
		});


	},
		function () {
			$('.triangle-left').delay(50).queue(function (next) {
				$(this).removeClass("darkback-left");
				next();
			});

			$('.triangle-right').delay(50).queue(function (next) {
				$(this).removeClass("darkback-right");
				next();
			});

		});

	$('.fb-star').mouseenter(function () {
	    $(this).addClass("fillstar");
	    $(this).css({ "font-size": "14px",
	                  "text-shadow": "-1px 0 #17b6e5, 0 1px #17b6e5, 1px 0 #17b6e5, 0 -1px #17b6e5",
	                  "cursor": "pointer"
	     });
	    $(this).prevAll('.fb-star').addClass('fillstar');
	    $(this).prevAll('.fb-star').css({ "font-size": "14px",
	                  "text-shadow": "none"
	     });

	    $(this).nextAll('.fb-star').removeClass('fillstar');
	    $(this).nextAll('.fb-star').css({ "font-size": "14px",
	                  "text-shadow": "none"
	     });

	});

	$('.fb-star').mouseleave(function () {

	    var selected = $(this).parent().find('[selected="selected"]');
	    if (selected.length > 0){
	        selected.addClass("fillstar");

	        selected.prevAll('.fb-star').addClass('fillstar');
            selected.prevAll('.fb-star').css({ "font-size": "14px",
                          "text-shadow": "none"
             });

            selected.nextAll('.fb-star').removeClass('fillstar');
            selected.nextAll('.fb-star').css({ "font-size": "14px",
                          "text-shadow": "none"
             });
	    }else{
	        $(this).parent().find('.fb-star').removeClass("fillstar");
	    }


	});

	$('.fb-star[title]').tooltip();

	$('.fb-star').on('click', function(){

	    $(this).parent().find('[selected="selected"]').removeAttr('selected');
	    $(this).attr('selected', 'selected');
	    $(this).addClass("fillstar");
	    $(this).prevAll('.fb-star').addClass('fillstar');
	    $(this).prevAll('.fb-star').css({ "font-size": "14px",
	                  "text-shadow": "none"
	     });
	    var field = $(this).parent().attr('class');
	    var txt = $(this).attr('data-original-title');
	    var val = $(this).attr('i');
	    addRating(field, txt, val);
	});

	$('.txtbox').focusin(function () {
		$(this).parent().find('.iconbox').css({ "padding-left": "35px" });
		$('.loginfailed').css('display', 'none');

	});
	$('.txtbox').focusout(function () {
		$(this).parent().find('.iconbox').css({ "padding-left": "50px" });
	});

	$('.txtbox').hover(function () {
		$(this).parent().find('.iconbox').css({ "color": "#0069d9" });
	},
		function () {
			$(this).parent().find('.iconbox').css({ "color": "#666666" });
		});

});

$(window).resize(resizeMiddle);