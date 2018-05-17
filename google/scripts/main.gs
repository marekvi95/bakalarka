function doGet(e) {
  var book = SpreadsheetApp.getActiveSpreadsheet();
  var masterSheet = book.getSheetByName("Konfigurace");
  var json = convertSheet2Json(masterSheet);
}

function onOpen() {
  SpreadsheetApp.getUi()
  .createMenu("Kamera")
  .addSeparator()
  .addItem("Log", "logInfo")
  .addItem("Obrazky", "myFiles")
  .addItem('Konfigurace', 'openConfigDialog')
  .addToUi();
}



function logInfo() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var text = '{\n';
  for (var i = 0; i < data.length; i++) {
    if (i+1==data.length) {
      text = text +'\t"'+data[i][0]+'": '  +'"'+data[i][1]+'"\n}';
    }
    else {
      text = text + '\t"'+data[i][0]+'": '  +'"'+data[i][1]+'",\n';
    }
  }

  file = DriveApp.getFileById('1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku');
  file.setContent(text);

  //DriveApp.createFile('konfigurace.json', text);

}

function myFiles()
{
  var ss=SpreadsheetApp.getActive();
  var sh=ss.getSheetByName('Obrazky');
  sh.clear();
  var folder = DriveApp.getFolderById('1AO_tQMMz2c6_l69s9vo9PW0PTy4nrYqi')
  var files = folder.getFiles();
  var s='';
  var cnt=1;
  while(files.hasNext())
  {
    var fi=files.next();
    var type=fi.getMimeType();

    if(type==MimeType.JPEG)
    {
      sh.appendRow([fi.getDateCreated(),fi.getName(),type,fi.getUrl(),'=IMAGE("https://drive.google.com/uc?export=view&id=' + fi.getId() + '",1)']);
      sh.setRowHeight(cnt++, 200);
    }
  }
}

/***************************************************
Script will send an email notification to you or other email addresses
when a file in a given Google folder has been added, or modified. 06-07-16
***************************************************/
function checkForChangedFiles() {

// edit this line below with the ID "XXXXXXXxxXXXwwerr0RSQ2ZlZms" of the folder you want to monitor for changes
  var folderID = '"' + "1AO_tQMMz2c6_l69s9vo9PW0PTy4nrYqi" + '"';

// Email Configuration
  var emailFromName ="Kamerový zapezpečovací systém (Neodpovídejte)";
  var emailSubject = "Registrován pohyb";
  var emailBody = "<br>Detekován pohyb<br>";
  var emailFooter = "Administrátor mv.marekvitula@gmail.com";

  var folderSearch = folderID + " " + "in parents";
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Obrazky');
  //var email = sheet.getRange("E1").getValue();
  var email = "mv.marekvitula@gmail.com";
  var timezone = ss.getSpreadsheetTimeZone();
  var today     = new Date();

  // Run script next day, and set below to 24 hours
  // 60 * 1000 = 60 second
  // 60* (60 * 1000) = 60 mins which is 1 hour
  // 24* (60* (60 * 1000)) = 1 day which 24 hours
  //var oneDayAgo = new Date(today.getTime() - 1 * 24 * 60 * 60 * 1000);
   var oneDayAgo = new Date(today.getTime() - 1 * 60 * 1000);

  var startTime = oneDayAgo.toISOString();

  var search = '(trashed = true or trashed = false) and '+ folderSearch +' and (modifiedDate > "' + startTime + '")';

  var files  = DriveApp.searchFiles(search);

  var row = "", count=0;

  while( files.hasNext() ) {

    var file = files.next();
    var fileName = file.getName();
    var fileURL  = file.getUrl();
    var lastUpdated =  Utilities.formatDate(file.getLastUpdated(), timezone, "yyyy-MM-dd HH:mm");
    var dateCreated =  Utilities.formatDate(file.getDateCreated(), timezone, "yyyy-MM-dd HH:mm")

    var type=file.getMimeType();

    if(type==MimeType.JPEG)
    {
      sheet.appendRow([file.getDateCreated(),file.getName(),type,file.getUrl(),'=IMAGE("https://drive.google.com/uc?export=view&id=' + file.getId() + '",1)']);
      sheet.setRowHeight(sheet.getLastRow(), 200);
      row += "<li>" + lastUpdated + " <a href='" + fileURL + "'>" + fileName + "</a></li>";
    }

    count++;
  }

  if (row !== "") {
    row = "<p>" + count + " fotografií bylo nasnímáno. Tady je seznam:</p><ol>" + row + "</ol>";
    row +=  emailBody+"<br>" + "<br><small> "+emailFooter+" </a>.</small>";
    MailApp.sendEmail(email, emailSubject, "", {name: emailFromName, htmlBody: row});
  }
}


function openConfigDialog() {
  var html = HtmlService.createHtmlOutputFromFile('index');
  SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
      .showModalDialog(html, 'Konfigurace');
}

function saveToFile(data) {
  file = DriveApp.getFileById('1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku');
  file.setContent(data);
  saveToSheets(data)
}

function saveToSheets(data) {
  var ss=SpreadsheetApp.getActive();
  var sh=ss.getSheetByName('Konfigurace');
  sh.getRange("F13").setValue(data)
}
