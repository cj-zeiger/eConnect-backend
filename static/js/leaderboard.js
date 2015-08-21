function updateStatus(){
  var service_status = $.ajax("/running/").done(function(data) {
    if(data == "Running"){
      $('#service_status').html('Service is running.');
    } else {
      $('#service_status').html('Service is not running.');
    }
  }).fail(function(data) {
    $('#service_status').html('Cannot connect to service.');
  });
}
$(document).ready(function(){
  $('#clear-modal').on('shown.bs.modal', function () {
    $('#myInput').focus()
  })
  $('#refresh-btn').click(function() {
    $('#table').bootstrapTable('refresh');
  });
  $('#start-btn').click(function(){
    $.ajax('/running/1').done(function(){
      updateStatus();
    }).fail(function() {
      alert('Unable to connect to service');
    });
  });
  $('#stop-btn').click(function(){
    $.ajax('/running/0').done(function(){
      updateStatus();
    }).fail(function() {
      alert('Unable to connect to service');
    });
  });
  $('#clear-btn').click(function(){
    $.ajax('/clear/').done(function(){
      location.reload();
    }).fail(function() {
      alert('Unable to connect to service');
    });
  });
  updateStatus();
});
$('#table').bootstrapTable({
    url: 'http://localhost:5000/users/json',
    columns: [{
        field: 'name',
        title: 'Name'
    }, {
        field: 'count',
        title: 'Connections'
    },]
});
