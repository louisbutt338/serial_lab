/*
alternative using arduino libraries (does not work)
*/
#include "SoftwareSerial.h"

SoftwareSerial rs232(10, 11);

const byte numChars = 64;
char receivedChars[numChars];

// create an array of pointers to commands
char *cmds[] = {"AT+CPIN?", "AT+CSQ", "AT+COPS?", "AT+CGMI", "AT+CGMM", "AT+CGSN"};

// two dimensional array to hold replies
char replies[sizeof(cmds) / sizeof(cmds[0])][numChars];

bool newData = false;

void setup()
{
  Serial.begin(250000);
  rs232.begin(9600);
  Serial.println("<Arduino is ready>");
}

void loop()
{
  // index of command to send
  static byte cmdIndex = 0;
  // flag indicating thhat we;re waiting for a reply
  static bool fWaiting4Reply = false;

  // if not waiting for reply
  if (fWaiting4Reply == false)
  {
    // if not all commands done
    if (cmdIndex < sizeof(cmds) / sizeof(cmds[0]))
    {
      Serial.print("Sending: "); Serial.println(cmds[cmdIndex]);
      // send command followed by '\r'
      rs232.print(cmds[cmdIndex]); rs232.print("\r");
      fWaiting4Reply = true;
    }
  }

  // if waiting for reply
  if (fWaiting4Reply == true)
  {
    getReply();
    if (newData == true)
    {
      processReply(cmdIndex);
      fWaiting4Reply = false;
      cmdIndex++;
    }
  }

  // if all commands done
  if (cmdIndex == sizeof(cmds) / sizeof(cmds[0]))
  {
    // debug print
    for (int replyCnt = 0; replyCnt < sizeof(cmds) / sizeof(cmds[0]); replyCnt++)
    {
      Serial.print("Reply "); Serial.print(replyCnt);
      Serial.print(" ["); Serial.print(replies[replyCnt]); Serial.println("]");
    }

    // wait forever
    for (;;);
  }
}

/*
  get reply from rs232
  NOTE: was recvWithStartEndMarkers
*/
void getReply()
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char endMarker = '\r';
  char rc;

  while (rs232.available() > 0 && newData == false)
  {
    rc = rs232.read();

    if (rc != endMarker)
    {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars)
      {
        ndx = numChars - 1;
      }
    }
    else
    {
      receivedChars[ndx] = '\0'; // terminate the string
      recvInProgress = false;
      ndx = 0;
      newData = true;
    }
  }
}

/*
  process reply
  NOTE: was showNewData
*/
void processReply(byte cmdNum)
{
  // copy data to reply buffer
  strcpy(replies[cmdNum], receivedChars);
  // indicate we're ready for next reply
  newData = false;
}