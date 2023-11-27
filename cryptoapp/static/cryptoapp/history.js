jQuery.noConflict();
jQuery(document).ready(function() {
	document.title='Simple DataTable';
	// DataTable initialisation
	jQuery('#example').DataTable(
		{
			"paging": false,
		}
	);

	//Delete buttons
	jQuery('.dt-delete').each(function () {
		jQuery(this).on('click', function(evt){
			let jQuerythis = jQuery(this);
			var dtRow = jQuerythis.parents('tr');
			if(confirm("Are you sure to delete this transaction?")){
				const table = jQuery('#example').DataTable();
				table.row(dtRow[0].rowIndex-1).remove().draw( false );
			}
		});
	});

});

