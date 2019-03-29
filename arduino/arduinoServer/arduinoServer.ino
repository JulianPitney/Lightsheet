#include <AccelStepper.h>
#include <CmdParser.hpp>
#include <Encoder.h>



/*
   When a valid command is received, it will be stored in this struct.
   Only one command is stored at a time (currect command is overwritten when
   new valid command is received and parsed.)
*/
struct CMD {

  uint16_t argc;
  String cmd;
  String* params = NULL;
};
struct CMD* command = new CMD;

// Serial command parser
CmdParser cmdParser;
// This timeout is in ms
uint32_t cmdParserTimeout = 10000;




// Arduino LED
const int LED = 13;
// Laser Enable
const int LASER_ENABLE = 6;


// Driver 1 config
const int DRIVER1_ENA = 4;
const int DRIVER1_DIR = 8;
const int DRIVER1_PUL = 7;
const int STEPPER1_MAX_SPEED = 4000.0;
const int STEPPER1_SPEED = 20.0;
const int STEPPER1_ACCELERATION = 400.0;
// Driver 2 config
const int DRIVER2_ENA = 12;
const int DRIVER2_DIR = 11;
const int DRIVER2_PUL = 10;
const int STEPPER2_MAX_SPEED = 4000.0;
const int STEPPER2_SPEED = 20.0;
const int STEPPER2_ACCELERATION = 400.0;
// Steppers
AccelStepper STEPPER1(AccelStepper::DRIVER, DRIVER1_PUL, DRIVER1_DIR);
AccelStepper STEPPER2(AccelStepper::DRIVER, DRIVER2_PUL, DRIVER2_DIR);
Encoder STEPPER1_ENCODER(2,3);
//Encoder STEPPER2_ENCODER(??,??);
//Encoder STEPPER3_ENCODER(??,??);


void setup() {

  // Block until serial connection established
  Serial.begin(57600);
  while(!Serial) {
    delay(100);
  }
  Serial.write("ARDUINO READY\n");
  pinMode(LED, OUTPUT);
  pinMode(LASER_ENABLE, OUTPUT);
  digitalWrite(LASER_ENABLE, LOW);


  // Setup STEPPER1
  STEPPER1.setMaxSpeed(STEPPER1_MAX_SPEED);
  STEPPER1.setSpeed(STEPPER1_SPEED);
  STEPPER1.setAcceleration(STEPPER1_ACCELERATION);
  STEPPER1.setEnablePin(DRIVER1_ENA);
  STEPPER1.setPinsInverted(false,false,true);
  STEPPER1.enableOutputs();
  // Setup STEPPER2
  STEPPER2.setMaxSpeed(STEPPER2_MAX_SPEED);
  STEPPER2.setSpeed(STEPPER2_SPEED);
  STEPPER2.setAcceleration(STEPPER2_ACCELERATION);
  STEPPER2.setEnablePin(DRIVER2_ENA);
  STEPPER2.setPinsInverted(false,false,true);
  STEPPER2.enableOutputs();
}



/*
    This function enables the outputs of <stepper> and moves
    it for <steps>. It then disables the outputs again.

    Note: The sign of <steps> determines the direction of rotation.
    Note: This function blocks until the movement is completed.
 */
void moveStepper(AccelStepper *stepper, int steps, int speed){

    stepper->move(steps);
    stepper->setSpeed(speed);
    while(stepper->targetPosition() != stepper->currentPosition())
    {
      stepper->runSpeedToPosition();
    }
}



/*
   This function listens on the USB serial port for a newline
   terminated command to arrive. The command is parsed and stored
   in the global struct CMD* <command>. The return code indicates
   one of three conditions:
    0 = New command received and stored in <command>
    1 = Listening timed out
   -1 = Parsing error

   Note: This command times out after <cmdParserTimeout> ms.
*/
int listenForCommandWithTimeout() {

    CmdBuffer<64> myBuffer;
    String cmd;
    uint16_t argc;
    String* params;



    if (myBuffer.readFromSerial(&Serial, cmdParserTimeout))
    {
        if (cmdParser.parseCmd(&myBuffer) != CMDPARSER_ERROR)
        {

            myBuffer.getStringFromBuffer();
            cmd = cmdParser.getCommand();
            argc = cmdParser.getParamCount();

            if(command->params != NULL)
            {
              delete[] command->params;
            }

            params = new String[argc];
            for (size_t i = 0; i < argc; i++)
            {
                params[i] = cmdParser.getCmdParam(i);
            }

            command->argc = argc;
            command->cmd = cmd;
            command->params = params;


            return 0;
        }
        else
        {
            Serial.println("Parser error!");
            return -1;
        }
    }
    else
    {
      return 1;
    }
}



/*
   This function runs the command stored in the global struct CMD* <command>.
   It identifies the command to be run, and ensures the correct number of parameters
   are present. Once this is confirmed, the appropriate command is called.

   Note: Implementing new commands involves adding an "else if" clause
   to this function that calls the new command (which also needs to be implemented).
*/
int runCommand() {

  int rc;

  if(command->cmd == "MOVE")
  {
      if(command->argc != 4)
      {
        sendResponse("Invalid number of parameters!");
        rc = -1;
      }
      else
      {
        rc = moveCommand();
      }
  }
  else if(command->cmd == "SET")
  {
      if(command->argc != 4)
      {
        sendResponse("Invalid number of parameters!");
        rc = -1;
      }
      else
      {
        rc = setCommand();
      }
  }
  else if(command->cmd == "GET")
  {
      if(command->argc != 3)
      {
        sendResponse("Invalid number of parameters!");
        rc = -1;
      }
      else
      {
        rc = getCommand();
      }
  }
  else if(command->cmd == "TOGGLE_LASER")
  {
    if(command->argc != 1)
    {
      sendResponse("Invalid number of parameters!");
      rc = -1;
    }
    else
    {
      rc = toggleLaserCommand();
      sendResponse("LASER_SET:" + String(rc));
    }
  }
  else
  {
      sendResponse("Invalid command!");
      rc = -2;
  }

  return rc;
}


/*
   This function implements the MOVE command. It will:
   1. Verify integrity and form of command.
   2. Identify which motor is to be moved.
   3. Identify how many steps to take and in which direction.
   4. Call the move function for the motor in question.
*/
int moveCommand() {

  int rc;
  AccelStepper *stepper;
  bool stepperExists = true;
  stepper = selectCorrectStepper();

  int steps = command->params[2].toInt();
  int speed = command->params[3].toInt();
  if(steps == 0)
  {
    sendResponse("Invalid STEPS value!");
    rc = -1;
  }

  if(stepperExists)
  {
    moveStepper(stepper, steps, speed);
    //sendResponse("MOVE:" + command->params[1] + ":" + command->params[2] + ":" + command->params[3]);
    rc = 0;
  }
  else
  {
    sendResponse("Requested stepper does not exist!");
    rc = -1;
  }

  return rc;
}


/*
  This function implements the SET command. It will:
  1. Verify the integrity and form of the command.
   2. Identify which motor's parameters are to be changed.
   3. Identify which parameter is to be changed.
   4. Change the requested parameter of the motor in question
        to the correct value.
*/
int setCommand() {

  int rc;
  AccelStepper *stepper;
  bool stepperExists = true;
  stepper = selectCorrectStepper();


  float parameterValue = command->params[3].toFloat();
  if(parameterValue == -1)
  {
    sendResponse("Invalid paramter value!");
    rc = -1;
  }


  if(stepperExists)
  {
    rc = setCorrectParameterValue(stepper, parameterValue);
  }
  else
  {
    sendResponse("Requested stepper does not exist!");
    rc = -1;
  }

  return rc;
}


/*
   This function implements the GET command. It will:
   1. Select the correct motor to get the parameter from.
   2. Identify which parameter to get.
   3. Write the parameter in question to the seria port.
*/
int getCommand() {

  int rc;
  AccelStepper *stepper;
  bool stepperExists = true;
  stepper = selectCorrectStepper();
  rc = getCorrectParameterValue(stepper);
  return rc;
}

int toggleLaserCommand() {

  int newState = !digitalRead(LASER_ENABLE);
  digitalWrite(LASER_ENABLE, newState);
  return newState;
}


/*
   Helper function for selecting the stepper motor requested by
   any of the command functions.
   Reads the global struct CMD* <command> and returns the correct
   stepper.
*/
AccelStepper* selectCorrectStepper() {

  if(command->params[1] == "S1")
  {
    return &STEPPER1;
  }
  else if(command->params[1] == "S2")
  {
    return &STEPPER2;
  }
  else
  {
    return NULL;
  }
}


/*
    Helper function for setting the selected parameter of the selected
    motor requested by the SET command. Receives the correct stepper
    and parameter value from setCommand() and sets correct parameter
    by checking the global struct CMD* <command>.

    Note: Also writes a command complete confirmation to the serial USB port.
    TODO: This should maybe be merged into setCommand().
 */
int setCorrectParameterValue(AccelStepper *stepper, float value) {

  if(command->params[2] == "SPEED") {

    stepper->setSpeed(value);
    sendResponse(command->params[1] + ":SET:SPEED:" + String(value));
    return 0;
  }
  else if(command->params[2] == "MAXSPEED")
  {
    stepper->setSpeed(value);
    sendResponse(command->params[1] + ":SET:MAXSPEED:" + String(value));
    return 0;
  }
  else if(command->params[2] == "ACCEL")
  {
    stepper->setAcceleration(value);
    sendResponse(command->params[1] + ":SET:ACCELERATION:" + String(value));
    return 0;
  }
  else
  {
    sendResponse("Requested parameter does not exist!");
    return -1;
  }


}

/*
    Helper function for getting the parameter of the motor requested by getCommand().
    Receives appropriate stepper from getCommand() and retrieves the parameter requested
    by the global struct CMD* <command>.

    Note: Writes the requested parameter to the serial USB pot.
    TODO: This should maybe be merged into getCommand().
 */


int getCorrectParameterValue(AccelStepper *stepper) {

  if(command->params[2] == "SPEED")
  {
    sendResponse(command->params[1] + ":SPEED:" + String(int(stepper->speed())));
    return 0;
  }
  else if(command->params[2] == "MAXSPEED")
  {
    sendResponse(command->params[1] + ":MAXSPEED:" + String(int(stepper->maxSpeed())));
    return 0;
  }
  else
  {
    sendResponse("Requested parameter does not exist!");
    return -1;
  }
}



/*
   Wrapper for writing to serial USB port in a way
   python3 will understand.
*/
void sendResponse(String response) {

  response += "\n";
  Serial.write(response.c_str());
}




void loop() {

  // New command received (0), Parse error (-1), Listening timed out (1)
  int rc = listenForCommandWithTimeout();
  switch(rc)
  {
    case 0:
      runCommand();
      break;
    case 1:
      // listening timeout
      break;
    case -1:
      // parse error
      break;
    default:
      break;
  }
}