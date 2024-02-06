(function ($) {
    "use strict";

	var navbarCollapse = function () {
		if ($("#menu").offset().top > 100) {
			$("#menu").addClass("navbar-shrink");

		} else {
			$("#menu").removeClass("navbar-shrink");

		}
	};
	navbarCollapse();
	$(window).scroll(navbarCollapse);
	$('input[name="carrier_select"]').click(function () {
		//$("#package-type").show();
		$("#package-type").fadeIn(500);
	});
	$('#manual-input-btn').click(function () {
		$("#automatic-input").hide();
		$("#manual-input").fadeIn(500);
		$(this).attr("class","btn btn-blue")
		$("#automatic-input-btn").attr("class","btn btn-blue-outline")
	});
	$('#automatic-input-btn').click(function () {
		$("#manual-input").hide();
		$("#automatic-input").fadeIn(500);
		$(this).attr("class","btn btn-blue")
		$("#manual-input-btn").attr("class","btn btn-blue-outline")
	});	
	$('input[id="dimensions"]').click(function () {

		if ($(this).is(":checked")) {
			$("#package-weight-lbs").hide();
			$("#package-weight-kg").fadeIn(500);
		} else {
			$("#package-weight-kg").hide();
			$("#package-weight-lbs").fadeIn(500);
		}
	});
	$(".country-select").change(function () {
		var to = $("#dim_tcountry").val();
        var from = $("#dim_fcountry").val();
		if (to !== null && from !== null) {
			if (to !== from && to !== 'select' && from !== 'select') {
				$(".customs").fadeIn(500);
			} else {
				$(".customs").hide();
			}
		}
    });
	
	$('.carrier').mouseup(function(){
		$("#carrier_"+$('input[name=carrier_select]:checked').val()).hide();
		//console.log(document.getElementById('dimensions').value);
	});
	$('input[name=carrier_select]').change(function(){
		$("#carrier_"+$('input[name=carrier_select]:checked').val()).fadeIn(500);
	});

})(jQuery);

(function() {

    const packageTypes = document.querySelectorAll('select[name="packagetype"]');

    if (packageTypes) {
        packageTypes.forEach(packageType => {
            packageType.onchange = event => changePackage(event);
        });
    }

    const carrierInputs = document.querySelectorAll('input[name="carrier_select"]');

    if (carrierInputs) {
        carrierInputs.forEach(carrierInput => {
            carrierInput.onchange = event => resetPackage(event);
        });
    }

    function copyToClipboard(elementId) {
        var aux = document.createElement("input");
        aux.setAttribute("value", document.getElementById(elementId).innerHTML);
        document.body.appendChild(aux);
        aux.select();
        document.execCommand("copy");
        document.body.removeChild(aux);
    }

    function resetPackage(event) {

        // let carrierInputs = document.querySelectorAll('input[name="carrier_select"]');

        // if (carrierInputs) {
        //     carrierInputs.forEach(carrierInput => {
        //         carrierInput.parentElement.style.pointerEvents = 'auto';
        //     });
        // }

        // if (event != null) {

        //     event.target.parentElement.style.pointerEvents = 'none';

        // }

        const packageType = document.querySelector('#packagetype');

        if (packageType) {

            for (var i = 0; i < packageType.options.length; i++) {
                const option = packageType.options[i];

                if (option.getAttribute('data-carrier') == event.target.value) {

                    document.getElementById("packagetype").selectedIndex = i;
                    break;
                }
            }

        }

        // document.getElementById("packagetype").selectedIndex = 0;
        // document.getElementById("carrier_ups_custommsg").innerHTML = "";
		// document.getElementById("carrier_usps_custommsg").innerHTML = "";
		// document.getElementById("carrier_fedex_custommsg").innerHTML = "";

    }

    function changePackage(event) {

        packagetypepre = document.getElementById("packagetype");

		$("#quotecontainer").html('');
        var fedex = 0;
        var ups = 0;
        var usps = 0;
		var dhl = 0;
        if (document.getElementById("usps").checked == true) { var packagetypepre = document.getElementById("packagetype"); ups, fedex, dhl = 0; usps = 1; }
        //if (document.getElementById("fedex").checked == true) { var packagetypepre = document.getElementById("packagetype"); ups, dhl, usps = 0; fedex = 1; }
        // if (document.getElementById("ups").checked == true) { var packagetypepre = document.getElementById("packagetype"); dhl, fedex, usps = 0; ups = 1; }
        if (document.getElementById("dhl").checked == true) { var packagetypepre = document.getElementById("packagetype"); ups, fedex, usps = 0; dhl = 1; }
        if (document.getElementById("canadapost").checked == true) {var packagetypepre = document.getElementById("packagetype"); }
        var packagetype = packagetypepre.value;
        var carrier_usps = 0;
        var carrier_fedex = 0;
        var carrier_ups = 0;
        var carrier_dhl = 0;

        // Requirements for each package.
        var reqs = [    0,    0,    0,    0,    0,    0,    0,    0,  ""];

        // =========================================================================================================================
        // USPS
        //                                                                  Minimum           Maximum          Max   Max
        //                                                                  L     W     H,    L     W     H    All  Weight
        // Packages
        if (packagetype == "custom" && usps == 1) { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, 0, 108, 1120, "Maximum size is 108\" in combined length and girth (distance around the thickest part)."]; }
        if (packagetype == "LargeParcel") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, 0, 130, 1120, "Maximum size is 130\" in combined length and girth (distance around the thickest part). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "Parcel") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, 0, 108, 1120, "Maximum size is 108\" in combined length and girth (distance around the thickest part). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "Softpack") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, 0, 108, 1120, ""]; }
        // Letters
        if (packagetype == "Card") { var carrier_usps = 1; var reqs = [3.5, 5.5, 1, 4.25, 6, 0, 0, 0, "Must be a flat surface. Maximum size is 4 1/4\" x 6\""]; }
        if (packagetype == "Letter") { var carrier_usps = 1; var reqs = [3.5, 5.5, 1, 6.125, 11.5, 0, 0, 3.5, "Must be a flat surface. Maximum weight is 3.5 oz."]; }
        if (packagetype == "Flat") { var carrier_usps = 1; var reqs = [6.125, 11.5, 0, 12, 15, 0, 0, 13, "Must be a flat surface. Maximum weight is 13 oz."]; }
        if (packagetype == "IrregularParcel") { var carrier_usps = 1; var reqs = [0, 0, 0, 26, 0, 0, 0, 16, "Rolls and tubes up to 26 inches long. Maximum weight is 16 oz."]; }
        // Flat Rate
        if (packagetype == "FlatRateEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Flat Rate Envelope (12 1/2\" x 9 1/2\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "FlatRateLegalEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Legal Flat Rate Envelope (15\" x 9 1/2\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "SmallFlatRateEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Small Flat Rate Envelope (10\" x 6\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "FlatRatePaddedEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Padded Flat Rate Envelope (12 1/2\" x 9-1/2\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "FlatRateGiftCardEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Gift Card Flat Rate Envelope (10\" x 7\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "FlatRateWindowEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Window Flat Rate Envelope (10\" x 5\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }
        if (packagetype == "FlatRateCardboardEnvelope") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Cardboard Flat Rate Envelope (12 1/2\" x 9-1/2\"). Contents must weigh less than 70 lbs. International Weight limit: 4 lbs."]; }

        if (packagetype == "SmallFlatRateBox") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Small Flat Rate Box (8 5/8\" x 5 3/8\" x 1 5/8\"). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "MediumFlatRateBox") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Medium Flat Rate Box (11\" x 8 1/2\" x 5 1/2\"). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "LargeFlatRateBox") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Large Flat Rate Box (12\" x 12\" x 5 1/2\"). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "LargeFlatRateBoardGameBox") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 70, "Must have pre-purchased USPS Large Flat Rate Board Game Box (23 11/16\" x 11 3/4\" x 3\"). Contents must weigh less than 70 lbs."]; }
        if (packagetype == "RegionalRateBoxA") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 15, "Dimensions 10 1/8\" x 7 1/8\" x 5\". Contents must weigh less than 15 lbs."]; }
        if (packagetype == "RegionalRateBoxB") { var carrier_usps = 1; var reqs = [0, 0, 0, 0, 0, -2, 0, 20, "Dimensions 12 1/4\" x 10 1/2\" x 5 1/2\". Contents must weigh less than 20 lbs."]; }

        // =========================================================================================================================
        // UPS
        //                                                                   Minimum           Maximum         Max   Max
        //                                                                   L     W     H,    L     W     H   All  Weight
        // Packages
        if (packagetype == "custom" && ups == 1){ var carrier_ups = 1; var reqs =     [    0,    0,    0,  108,  108,  108,  165, 2400,  " "]; }
        if (packagetype == "UPS_Box_25kg"){ var carrier_ups = 1; var reqs =     [    0,    0,    0,    0,    0,   -3,    0,  880,  "Must have pre-purchased UPS 25kg(55lbs) Box (19.75in x 17.75in x 13.25in)"];  }
        if (packagetype == "UPS_Box_10kg"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,  352,  "Must have pre-purchased UPS 10kg(22lbs) Box (16.5in x 13.25in x 10.75in)"];  }
        if (packagetype == "UPS_Express_Tube"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,    0,  "Must have pre-purchased UPS Triangular tube for rolled papers (38in x 6in x 6in)"];  }
        if (packagetype == "UPS_Express_Pak"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,    0,  "Must have pre-purchased UPS Pak (16in x 12.75 in)"];  }
        if (packagetype == "UPS_Pallet"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,24000,  "Cargo secured to a shipping pallet. More than 150 lbs."];  }
        if (packagetype == "UPS_Express_Box_Small"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,  480,  "Must have pre-purchased UPS Small Express Box (12.5in x 3.75in x 18in)"];  }
        if (packagetype == "UPS_Express_Box"){ var carrier_ups = 1; var reqs  =    [    0,    0,    0,    0,    0,   -3,    0,  480,  "Must have pre-purchased UPS Express Box (13in x 11in x 2in)"];  }
        if (packagetype == "UPS_Express_Box_Medium"){ var carrier_ups = 1; var reqs =    [    0,    0,    0,    0,    0,   -3,    0,  480,  "Must have pre-purchased UPS Medium Express Box (16in x 11in x 3in)"];  }
        if (packagetype == "UPS_Express_Box_Large"){ var carrier_ups = 1; var reqs =    [    0,    0,    0,    0,    0,   -3,    0,  480,  "Must have pre-purchased UPS Large Express Box (18in x 13in x 3in)"];  }

        // =========================================================================================================================
        // DHL
        //                                                                   Minimum           Maximum         Max   Max
        //                                                                   L     W     H,    L     W     H   All  Weight
        // Packages
        if (packagetype == "custom" && dhl == 1) { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,    0,    0,    0,  ""]; }
        if (packagetype == "DHLeC_Irregular") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -3,    0,    70,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "DHLeC_SM_Flats") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -3,    0,    70,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl4") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl5") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl6") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl7") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl8") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl9") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl10") { var carrier_dhl = 1; var reqs =   [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl11") { var carrier_dhl = 1; var reqs =   [    0,    0,    0,    0,    0,   -2,    0,    0,  "Flat Rate Boxes/Envelope prices depend on the weight and zone they are shipped to."]; }
        if (packagetype == "dhl2") { var carrier_dhl = 1; var reqs =    [    0,    0,    0,    0,    0,   -1,    0,    0,  ""]; }
	
	
	
		if (packagetype == "custom" && fedex == 1) { var carrier_fedex = 1; var reqs =    [    0,    0,    0,    0,    0,    0,    0,    0,  ""]; }
        
        // =========================================================================================================================
        // CanadaPost
        //                                                                      Minimum           Maximum         Max   Max
        //                                                                      L     W     H,    L     W     H   All  Weight
        // Packages
        /*if (packagetype == "cp1") { var carrier_canadapost = 1; var reqs = [    0,    0,    0,    0,    0,    0,    0,    0,  ""]; }
        if (packagetype == "cp2") { var carrier_canadapost = 1; var reqs = [    0,    0,    0,    0,    0,   -1,    0,    0,  ""]; } */


        // Set requirements for form validation
        document.getElementsByName("xreqs").value = reqs;

        // Set custom message from data above
        if (carrier_usps == 1) {
            document.getElementById('carrier_usps_custommsg').innerHTML = reqs[8];
            document.getElementById('carrier_usps_custommsg').innerText = reqs[8];
            document.getElementById('carrier_usps_custommsg').textContent = reqs[8];

            // document.getElementById('carrier_usps').style.display = "block";
            // document.getElementById('carrier_fedex').style.display = "none";
            // document.getElementById('carrier_ups').style.display = "none";
            // document.getElementById('carrier_dhl').style.display = "none";
            // document.getElementById('carrier_canadapost').style.display = "none";
        } else if (carrier_fedex == 1) {
            
            msg = "Phone number is required for FedEx shipments. " + reqs[8];

            document.getElementById('carrier_fedex_custommsg').innerHTML = msg;
            document.getElementById('carrier_fedex_custommsg').innerText = msg;
            document.getElementById('carrier_fedex_custommsg').textContent = msg;
            
            // document.getElementById('carrier_usps').style.display = "none";
            // document.getElementById('carrier_fedex').style.display = "block";
            // document.getElementById('carrier_ups').style.display = "none";
            // document.getElementById('carrier_dhl').style.display = "none";
            // document.getElementById('carrier_canadapost').style.display = "none";
        } else if (carrier_ups == 1) {
            document.getElementById('carrier_ups_custommsg').innerHTML = reqs[8];

            document.getElementById('carrier_ups_custommsg').innerText = reqs[8];
            document.getElementById('carrier_ups_custommsg').textContent = reqs[8];

            // document.getElementById('carrier_usps').style.display = "none";
            // document.getElementById('carrier_fedex').style.display = "none";
            // document.getElementById('carrier_ups').style.display = "block";
            // document.getElementById('carrier_dhl').style.display = "none";
            // document.getElementById('carrier_canadapost').style.display = "none";
        }  else if (carrier_dhl == 1) {
            msg = "Phone number is required for DHL shipments. " + reqs[8];

            document.getElementById('carrier_dhl_custommsg').innerHTML = reqs[8];
            document.getElementById('carrier_dhl_custommsg').innerText = reqs[8];
            document.getElementById('carrier_dhl_custommsg').textContent = reqs[8];

            // document.getElementById('carrier_usps').style.display = "none";
            // document.getElementById('carrier_fedex').style.display = "none";
            // document.getElementById('carrier_ups').style.display = "none";
            // document.getElementById('carrier_dhl').style.display = "block";
            // document.getElementById('carrier_canadapost').style.display = "none";
        } /* else if (carrier_canadapost == 1) {
            //msg = "Coming soon! Please use USPS or UPS for now!"

            document.getElementById('carrier_canadapost_custommsg').innerHTML = reqs[8];
            document.getElementById('carrier_canadapost_custommsg').innerText = reqs[8];
            document.getElementById('carrier_canadapost_custommsg').textContent = reqs[8];

            document.getElementById('carrier_usps').style.display = "none";
            document.getElementById('carrier_fedex').style.display = "none";
            document.getElementById('carrier_ups').style.display = "none";
            document.getElementById('carrier_dhl').style.display = "none";
            document.getElementById('carrier_canadapost').style.display = "block";
        }*/

        // Do not show fields if they are not needed
        // Height
        if (reqs[5] == -1) {
			$('.dimensions-table').addClass('d-block').removeClass('d-none');
            $('#length_block').removeClass('d-none').addClass('d-block');
            $('#width_block').removeClass('d-none').addClass('d-block');
            $('#height_block').removeClass('d-block').addClass('d-none');
            $('#lbs_block').removeClass('d-none').addClass('d-block');
            $('#oz_block').removeClass('d-none').addClass('d-block');
            $('#kg_block').removeClass('d-none').addClass('d-block');
        } else if (reqs[5] == -2) {
            $('.dimensions-table').addClass('d-none').removeClass('d-block');
            $('#length_block').addClass('d-none').removeClass('d-block');
            $('#width_block').addClass('d-none').removeClass('d-block');
            $('#height_block').addClass('d-none').removeClass('d-block');
            $('#lbs_block').addClass('d-none').removeClass('d-block');
            $('#oz_block').addClass('d-none').removeClass('d-block');
            $('#kg_block').addClass('d-none').removeClass('d-block');
        } else if (reqs[5] == -3) {
			$('.dimensions-table').addClass('d-block').removeClass('d-none');
            $('#length_block').addClass('d-none').removeClass('d-block');
            $('#width_block').addClass('d-none').removeClass('d-block');
            $('#height_block').addClass('d-none').removeClass('d-block');
            $('#lbs_block').addClass('d-block').removeClass('d-none');
            $('#oz_block').addClass('d-block').removeClass('d-none');
            $('#kg_block').addClass('d-block').removeClass('d-none');
        } else {
			$('.dimensions-table').addClass('d-block').removeClass('d-none');
            $('#length_block').addClass('d-block').removeClass('d-none');
            $('#width_block').addClass('d-block').removeClass('d-none');
            $('#height_block').addClass('d-block').removeClass('d-none');
            $('#lbs_block').addClass('d-block').removeClass('d-none');
            $('#oz_block').addClass('d-block').removeClass('d-none');
            $('#kg_block').addClass('d-block').removeClass('d-none');
        }
    }

    const customsAdd = document.querySelector('.js-add');

    if (customsAdd) {
        customsAdd.onclick = addCustomsItem;
    }

    const customsRemove = document.querySelector('.js-remove');

    if (customsRemove) {
        customsRemove.onclick = removeCustomsItem;
    }

    function addCustomsItem() {
        var cst_error = "";
        
        var cst_qty = document.getElementsByName("customs_editor_quantity")[0].value;
        if (cst_qty == "") { cst_error = cst_error + "Please enter Quantity. "; }
        var cst_hs_tariff_number = document.getElementsByName("hs_tariff_number")[0].value;
        // if (cst_hs_tariff_number == "") { cst_error = cst_error + "Please enter Hs Tariff Number. "; }
        var cst_dsc = document.getElementsByName("customs_editor_desc")[0].value;
        if (cst_dsc == "") { cst_error = cst_error + "Please enter Description. "; }
        var cst_val = document.getElementsByName("customs_editor_value")[0].value;
        //if (cst_val == "") { cst_error = cst_error + "Please enter the value of the item higher than 0. "; }
        if (Number(cst_val) < 0.01) {cst_error = cst_error + "Please enter the value of the item (Must be higher than 0). ";}
        var cst_wgt = document.getElementsByName("customs_editor_weight")[0].value;
        //if (cst_wgt == "") { cst_error = cst_error + "Please enter the weight of the item. "; }
        if (Number(cst_wgt) < 0.01) {cst_error = cst_error + "Please enter the weight of the item (Must be higher than 0). ";}
        // var cst_tar = document.getElementsByName("customs_editor_tariff")[0].value;        
        var e = document.getElementById("customs_editor_origin");
        var cst_ori = e.options[e.selectedIndex].value;
        if (cst_ori == "") { cst_error = cst_error + "Please enter the origin of the item. "; }
        
        document.getElementById('customs_msg').innerHTML = cst_error;
        document.getElementById('customs_msg').innerText = cst_error;
        document.getElementById('customs_msg').textContent = cst_error;
        
        if (cst_error == "") {
            customs_values = document.getElementById('customs_values');

            const items = document.querySelector('.js-items');

            if (items) {

                const template = document.getElementsByClassName('js-item-template')[0];

                const item = template.cloneNode(true);

                const id = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

                item.setAttribute('data-id', id);

                item.getElementsByClassName('js-quantity')[0].setAttribute('value', cst_qty);
                item.getElementsByClassName('js-hs-tariff-number')[0].setAttribute('value', cst_hs_tariff_number);
                item.getElementsByClassName('js-description')[0].setAttribute('value', cst_dsc);
                item.getElementsByClassName('js-value')[0].setAttribute('value', cst_val);
                item.getElementsByClassName('js-weight')[0].setAttribute('value', cst_wgt);
                item.getElementsByClassName('js-origin')[0].setAttribute('value', cst_ori);

                let option = null;

                let dimensions_type = document.getElementById('dimensions').checked ? 'g' : 'oz';

                if (cst_hs_tariff_number) {
                    //Tariff # provided
                    option = new Option(cst_qty + 'x ' + cst_dsc + " (made in " + cst_ori + ", $" + cst_val + " total value, " + cst_wgt + dimensions_type + " total, tariff #" + cst_hs_tariff_number + ")", (cst_qty + ",`" + cst_ori + ",`" + cst_dsc + ",`" + cst_val + ",`" + cst_wgt + ",`" + cst_hs_tariff_number));
                } else {
                    //Tariff # not provided
                    option = new Option(cst_qty + 'x ' + cst_dsc + " (made in " + cst_ori + ", $" + cst_val + " total value, " + cst_wgt + dimensions_type + " total)", (cst_qty + "," + cst_ori + "," + cst_dsc + "," + cst_val + "," + cst_wgt));
                }

                option.setAttribute('data-id', id);

                customs_values.options[customs_values.options.length] = option;

                item.classList.remove('js-item-template');

                item.classList.add('js-item');

                items.appendChild(item);

            }

            weightCustomsDeclarationText();
        }
    }

    function removeCustomsItem() {
        
        var packageweight = totalOrderWeight();
        var select = document.getElementById('customs_values');

        if (select == null || select.selectedIndex == null || select.options[select.selectedIndex] == null) {
            return;
        }
        var id = select.options[select.selectedIndex].getAttribute('data-id');

        const items = document.querySelector('.js-items');

        if (items) {
            items.querySelector('div[data-id="' + id + '"]').remove();
        }

        value = select.selectedIndex;

        select.removeChild(select[value]);

        weightCustomsDeclarationText();

    }

    function weightCustomsDeclarationText() {
        var dimensions_type = document.getElementById('dimensions').checked;
        if (!dimensions_type) {
            $('#customs_totalweight').html('Total weight: '+weightCustomsDeclaration()+'oz (You set your package weight as '+totalOrderWeight()+'oz)');
        } else {
            $('#customs_totalweight').html('Total weight: '+weightCustomsDeclaration()+'g (You set your package weight as '+totalOrderWeight()+'g)');
        }
    }

    function weightCustomsDeclaration() {
        var weight = 0;
        const items = document.querySelector('.js-items');

        if (items) {

            let data = items.querySelectorAll('.js-item');

            data.forEach(item => {
                weight += Number(item.querySelector('.js-weight').value);
            });

        }

        return weight;
    }

    function totalOrderWeight() {
        var total_weight = 0;
		var dimensions_type = document.getElementById('dimensions').checked;
        if(!dimensions_type) {
            var lbs = parseFloat($('input[name=package_weight_lbs]').val());
            var oz = parseFloat($('input[name=package_weight_oz]').val());
            if(isNaN(lbs)) lbs = 0;
            if(isNaN(oz)) oz = 0;
            total_weight = lbs*16 + oz;
        } else {
            var kg = parseFloat(document.querySelector('input[name="package_weight_kg"]').value);
            if(isNaN(kg)) kg = 0;
            total_weight = kg*1000;
        }

        return total_weight;
    }

    // $('#usps').click();

    /*const selectedMailOption = document.querySelector('input[data-checked]');
    const main = document.querySelector('#main');

    if (selectedMailOption == null || main.getAttribute('data-package-type') == '' || main.getAttribute('data-carrier') == '') {

        $('#usps').click();
        
    } else {

        if (document.getElementById('carrier_usps') == null) {
            return;
        }

        document.getElementById('carrier_usps').style.display = "none";
        document.getElementById('carrier_fedex').style.display = "none";
        document.getElementById('carrier_ups').style.display = "none";
        document.getElementById('carrier_dhl').style.display = "none";
        document.getElementById('carrier_canadapost').style.display = "none";

        $('#' + main.getAttribute('data-carrier')).click();

        var event = new Event('change');
        selectedMailOption.dispatchEvent(event);

        setTimeout(() => {

            const option = document.querySelector('div[style=""] > select#packagetype');
    
            if (option) {
                let key = main.getAttribute('data-package-type');
    
                if (key != null && key != '') {
                    option.value = key;
    
                    option.onchange();

                    var event = new Event('change');
                    option.dispatchEvent(event);
                }
            }

        }, 800);
    }*/

})();