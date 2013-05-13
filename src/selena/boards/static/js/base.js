var Base = {
	reloadDashboard: function(){
		setTimeout(function() {location.reload(true);}, 60000);
	},

	dropdown: function(){
		$('.dropdown-toggle').dropdown();
	}
}

$(document).ready(function() {
	Base.dropdown();
});