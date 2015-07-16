function fetchSeries(url) {
    $.ajax({
	    url: url,

	    datatype: "json",

	    beforeSend: function(hdr) {
		  	var chart = $('#container').highcharts();
	    	chart.showLoading("Gegevens ophalen...");
	    	return true;
	    },
	    
		success: function(data) {
		  	var chart = $('#container').highcharts();
			var key = "grid";
		  	var series = chart.get(key);
			series.setData(data[key]);
	    },

	    error: function(hdr,status,errorThrown) {
	    	alert("Fout tijdens laden van tijdreeks: " + errorThrown);
	    },

	    complete: function(hdr, status) {
		  	var chart = $('#container').highcharts();
	    	chart.hideLoading();
	    }
    });
}
