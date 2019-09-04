/**
 * Update HandPeilingen when selected reference changes 
 */
(function($) {
	$(document).ready(function() {
		$("#id_refpnt").change(function () {
			  const $sel = $(this).find('option:selected');
			  const val = $sel.val();
			  const ref = $sel.text();
			  if (confirm(`Referentiepunt veranderd naar ${ref}.\nMeetwaarden aanpassen?`)) {
				  // TODO first save current edits...
				  // find out id of current instance from url
				  const reg = /\/(\d+)\/\w+/g;
				  const url = window.location.href;
				  const match = reg.exec(url);
				  if (match) {
					  const id = match[1];
					  window.location.href = `/net/ref/${id}?ref=${val}&next=${url}`;
				  }
			  }
		})
	})
})(grp.jQuery);