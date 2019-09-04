/**
 * Update HandPeilingen when selected reference changes 
 */
(function($) {
	$(document).ready(function() {
		$("#id_refpnt").change(function () {
			  const $sel = $(this).find('option:selected');
			  const val = $sel.val();
			  const ref = $sel.text();
			  if (confirm(`Referentie veranderd naar ${ref}\nMeetwaarden aanpassen?`)) {
				  // TODO first save current edits...
				  const reg = /\/(\d+)\/\w+/g;
				  const url = window.location.href;
				  const match = reg.exec(url);
				  if (match) {
					  const id = match[1];
					  window.location.href = `/net/ref/${id}?ref=${val}&next=${url}`;
				  }
			  }
//		  const bkb = parseFloat($("#id_bkb").val());
//		  console.debug(bkb);
//		  const ref = $(this).find('option:selected').text();
//		  if (confirm(`Referentie veranderd naar ${ref}\nMeetwaarden aanpassen?`)) {
//			  $("#datapoints-group").find(".grp-td.value input").each((i,el) => {
//				  if (el.value) {
//					  el.value = (bkb - parseFloat(el.value)).toString();
//					  console.debug(el.value);
//				  }
//			  });
//		  }
		})
	})
})(grp.jQuery);