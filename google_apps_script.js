// Paris Comedy — Google Apps Script
// ============================================================
// Paste into script.google.com (Tools > Script editor)
// Deploy as Web App:
//   Execute as: Me
//   Who has access: Anyone
// After deploying, copy the Web App URL → use as APPS_SCRIPT_URL in HTML files
// ============================================================

var NOTIFY_EMAIL = 'chucklericain@gmail.com';
var SHEET_ID = 'SHEET_ID'; // Replace with actual spreadsheet ID
var LEADS_TAB = 'Leads';

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var type = data._type || 'unknown';
    var timestamp = new Date().toISOString();

    var subject = '';
    var body = '';
    var autoReplySubject = '';
    var autoReplyBody = '';
    var tier = 'free';

    // ── GIVEAWAY CLAIM ────────────────────────────────────────
    if (type === 'giveaway_claim') {
      subject = '🎉 Giveaway claim — ' + (data.show_name || 'Unknown');
      body = 'NEW GIVEAWAY CLAIM — activate Featured listing in venues.json\n\n'
        + 'Show name: ' + (data.show_name || '') + '\n'
        + 'Venue: ' + (data.venue || '') + '\n'
        + 'Day / Time: ' + (data.day_time || '') + '\n'
        + 'Eventbrite URL: ' + (data.eventbrite_url || 'Not provided') + '\n'
        + 'Video URL: ' + (data.video_url || 'Not provided') + '\n'
        + 'Contact Email: ' + (data.email || '') + '\n\n'
        + '→ Action: add to venues.json with tier: "featured", featured: true, verified: true\n'
        + '→ Increment giveaway_slots_used in venues.json';

      autoReplySubject = 'You\'re in the first 100! — Paris Comedy Featured listing';
      autoReplyBody = 'Hi,\n\nYou\'re confirmed in the first 100 Featured listings on Paris Comedy.\n\n'
        + 'Your Featured listing goes live within 24 hours. No payment is needed — this is part of our launch giveaway.\n\n'
        + 'What you\'ll get:\n'
        + '✓ Gold-highlighted card at top of results\n'
        + '✓ Verified badge\n'
        + '✓ Video clip embedded (if you provided a URL)\n'
        + '✓ Top placement in search results\n\n'
        + 'We\'ll email you again when your listing is live.\n\n'
        + '— Robert\n'
        + 'pariscomedy.com | payments@pariscomedy.com';

      tier = 'featured-free';

    // ── SHOW LISTING ──────────────────────────────────────────
    } else if (type === 'show_listing') {
      subject = '[Paris Comedy] New Show Listing — ' + (data.show_name || 'Unknown');
      body = 'New show listing submission:\n\n'
        + 'Show name: ' + (data.show_name || '') + '\n'
        + 'Venue: ' + (data.venue || '') + '\n'
        + 'Day: ' + (data.day || '') + '\n'
        + 'Time: ' + (data.time || '') + '\n'
        + 'Eventbrite URL: ' + (data.eventbrite_url || 'Not provided') + '\n'
        + 'Contact Email: ' + (data.email || '') + '\n';

      autoReplySubject = 'Show listed — Paris Comedy';
      autoReplyBody = 'Hi,\n\nYour show has been received and will be reviewed within 24 hours.\n\n'
        + 'Want Featured placement while it\'s still free? Reply to this email with your show details and we\'ll upgrade you at no cost.\n\n'
        + '— Robert\n'
        + 'pariscomedy.com';

      tier = 'free';

    // ── COMEDIAN BIO ──────────────────────────────────────────
    } else if (type === 'comedian_bio') {
      subject = '[Paris Comedy] New Comedian Bio — ' + (data.name || 'Unknown');
      body = 'New comedian bio submission:\n\n'
        + 'Name: ' + (data.name || '') + '\n'
        + 'Email: ' + (data.email || '') + '\n'
        + 'Experience: ' + (data.experience_level || 'Not specified') + '\n'
        + 'Style: ' + (data.style || 'Not specified') + '\n'
        + 'Video URL: ' + (data.video_url || 'Not provided') + '\n'
        + 'Bio:\n' + (data.bio || '') + '\n';

      autoReplySubject = 'Bio received — Paris Comedy';
      autoReplyBody = 'Hi ' + (data.name || '') + ',\n\n'
        + 'Got it. We\'ll review your bio and connect you with Paris bookers within 48 hours.\n\n'
        + '— Robert\n'
        + 'pariscomedy.com';

      tier = 'comedian';

    // ── BOOKING REQUEST ───────────────────────────────────────
    } else if (type === 'booking_request') {
      subject = '💰 Booking request — ' + (data.event_type || 'Unknown') + ' — ' + (data.budget || 'Budget TBD');
      body = 'HIGH PRIORITY — New booking request:\n\n'
        + 'Name: ' + (data.name || '') + '\n'
        + 'Email: ' + (data.email || '') + '\n'
        + 'Event type: ' + (data.event_type || '') + '\n'
        + 'Date: ' + (data.date || 'Not specified') + '\n'
        + 'Budget: ' + (data.budget || 'Not specified') + '\n'
        + 'Location: ' + (data.location || 'Not specified') + '\n';

      autoReplySubject = 'Booking request received — Paris Comedy';
      autoReplyBody = 'Hi ' + (data.name || '') + ',\n\n'
        + 'Thanks for reaching out. Robert will be in touch within 24 hours.\n\n'
        + '— Paris Comedy\n'
        + 'pariscomedy.com | payments@pariscomedy.com';

      tier = 'booking';

    // ── LEGACY / FALLBACK ─────────────────────────────────────
    } else if (type === 'booking') {
      subject = '[Paris Comedy] Booking Request — ' + (data.name || 'Unknown');
      body = 'Booking request:\n\n' + JSON.stringify(data, null, 2);
      tier = 'booking';

    } else if (type === 'listing') {
      subject = '[Paris Comedy] Show Listing — ' + (data.showname || 'Unknown');
      body = 'Show listing:\n\n' + JSON.stringify(data, null, 2);
      tier = 'free';

    } else if (type === 'bio') {
      subject = '[Paris Comedy] Comedian Bio — ' + (data.name || 'Unknown');
      body = 'Comedian bio:\n\n' + JSON.stringify(data, null, 2);
      tier = 'comedian';

    } else {
      subject = '[Paris Comedy] New Submission — type: ' + type;
      body = 'Raw submission:\n\n' + JSON.stringify(data, null, 2);
    }

    // Send notification to Robert
    GmailApp.sendEmail(NOTIFY_EMAIL, subject, body);

    // Send auto-reply to claimant (if we have their email)
    var claimantEmail = data.email || '';
    if (claimantEmail && autoReplySubject) {
      try {
        GmailApp.sendEmail(claimantEmail, autoReplySubject, autoReplyBody, {
          from: NOTIFY_EMAIL,
          replyTo: NOTIFY_EMAIL
        });
      } catch(replyErr) {
        // Log but don't fail the whole request
        Logger.log('Auto-reply failed: ' + replyErr.message);
      }
    }

    // Append to Leads sheet
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sheet = ss.getSheetByName(LEADS_TAB);
    if (!sheet) {
      sheet = ss.insertSheet(LEADS_TAB);
      sheet.appendRow(['Timestamp', 'Type', 'Name', 'Email', 'Show/Event', 'Message', 'Tier', 'Status', 'Source']);
    }

    var name = data.name || data.show_name || data.showname || '';
    var email = data.email || '';
    var showEvent = data.event_type || data.show_name || data.showname || data.company || '';
    var message = data.bio || data.message || data.style || '';

    sheet.appendRow([timestamp, type, name, email, showEvent, message, tier, 'New', 'pariscomedy.com']);

    return ContentService
      .createTextOutput(JSON.stringify({ok: true}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ok: false, error: err.message}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ok: true, service: 'Paris Comedy Lead Router', ts: new Date().toISOString()}))
    .setMimeType(ContentService.MimeType.JSON);
}
