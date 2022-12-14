$(function () {
    var $region_from = $('[name="region"]'),
        $district_from = $('[name="district"]'),
        $city_from = $('[name="city"]'),
        $street_from = $('[name="street"]'),
        $building_from = $('[name="building"]');

    var $region_to = $('[name="region2"]'),
        $district_to = $('[name="district2"]'),
        $city_to = $('[name="city2"]'),
        $street_to = $('[name="street2"]'),
        $building_to = $('[name="building2"]');

    $region_from.fias('type', $.fias.type.region);
    $region_from.fias('parentInput', '.js-form-address');
    $district_from.fias('type', $.fias.type.district);
    $district_from.fias('parentInput', '.js-form-address');
    $city_from.fias('type', $.fias.type.city);
    $city_from.fias('parentInput', '.js-form-address');
    $street_from.fias('type', $.fias.type.street);
    $street_from.fias('parentInput', '.js-form-address');
    $building_from.fias('type', $.fias.type.building);
    $building_from.fias('parentInput', '.js-form-address');
    $region_to.fias('type', $.fias.type.region);
    $region_to.fias('parentInput', '.js-form-address2');
    $district_to.fias('type', $.fias.type.district);
    $district_to.fias('parentInput', '.js-form-address2');
    $city_to.fias('type', $.fias.type.city);
    $city_to.fias('parentInput', '.js-form-address2');
    $street_to.fias('type', $.fias.type.street);
    $street_to.fias('parentInput', '.js-form-address2');
    $building_to.fias('type', $.fias.type.building);
    $building_to.fias('parentInput', '.js-form-address2');

  $.fias.setDefault({
        verify: true,
        change: function (obj) {
            if (obj) {
                setLabel($(this), obj.type);
                if(obj.parents){
                    $.fias.setValues(obj.parents, parentInput);
                }
            }
            log(obj);
            addressUpdate();
            mapUpdate();
        },
        checkBefore: function () {
            var $input = $(this);

            if (!$.trim($input.val())) {
                log(null);
                addressUpdate();
                mapUpdate();
                return false;
            }
        }
    });

    // Включаем получение родительских объектов для населённых пунктов
    $district_from.fias('withParents', true);
    $city_from.fias('withParents', true);
    $street_from.fias('withParents', true);

    $district_to.fias('withParents', true);
    $city_to.fias('withParents', true);
    $street_to.fias('withParents', true);

    // Отключаем проверку введённых данных для строений
    $building_from.fias('verify', false);
    $building_to.fias('verify', false);

    function setLabel($input, text) {
        text = text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
        $input.parent().find('label').text(text);
    }

    function addressUpdate() {
        var address = $.fias.getAddress('.js-form-address');
    //    var address2 = $.fias.getAddress('.js-form-address2');
        $('#address').text(address);
      //  $('#address2').text(address2);
    }

    function log(obj) {
        var $log, i;

        $('.js-log li').hide();

        for (i in obj) {
            $log = $('#' + i);

            if ($log.length) {
                $log.find('.value').text(obj[i]);
                $log.show();
            }
        }
    }
});