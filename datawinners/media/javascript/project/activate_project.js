$(document).ready(function(){
   $("#activate_project_block").dialog({
        title: gettext("Activate this Project?"),
        modal: true,
        autoOpen: false,
        height: 200,
        width: 300,
        closeText: 'hide'
      }
   );
   $(".activate_project").bind("click", function(){
       $("#activate_project_block").dialog("open");
       $('#confirm').attr('href',$(this).attr('href'));
       return false;
   });
   $("#activate_project_block .cancel_link").bind("click", function(){
         $("#activate_project_block").dialog("close");
   });
});
