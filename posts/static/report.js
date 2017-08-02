window.onload = function() {
	$("input[name=report]")[0].onclick = function(e) {
		$.ajax({
			url: '',
			type: "POST",
			data: $('form[name=postcontrols]').serialize()+'&report=Report',
			success: function(data, textStatus, jqXHR) {
				alert('Скаргу надіслано!');
			},
			error: function(jqXHR, textStatus, errorThrown) {
				alert('Щось пішло не так');
			}
		});
		e.preventDefault(); //STOP default action
	};
};
