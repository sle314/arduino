#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>
#include <TinkerKit.h>

YunServer server;
unsigned long timer;
TKThermistor therm(I0);

void setup() {
  Serial.begin(9600);

  // Bridge startup
  pinMode(13,OUTPUT);
  digitalWrite(13, HIGH);
  Bridge.begin();
  digitalWrite(13, LOW);

  // Osluskuj klijente iz lokalne mreze
  server.listenOnLocalhost();
  server.begin();
}

void loop() {

  // Prihvacaj klijente
  YunClient client = server.accept();

  // Ako se klijent spojio
  if (client) {
    // Obradi zahtjev
    obradi(client);

    // Zatvori konekciju i oslobodi resurse
    client.stop();
  }
  
  // Ponovi nakon 50ms, umjesto odmah
  delay(50);
}

void obradi(YunClient klijent){

  // Procitaj o kojem se uredaju radi
  String device = klijent.readStringUntil('/');

  // ako je uredaj tinkerkit pozovi metodu za obradu tinkerkita
  if (device == "tinkerkit"){
    tinkerkitReq(klijent);
  }

  // ako je uredaj sam yun pozovi metodu za obradu yuna
  else if (device == "yun"){
    yunReq(klijent);
  }

  // ako se radi o promjeni nacina rada pina pozovi modeCommand
  else if (device == "mode"){
    modeCommand(klijent);
  }
  
  else{
    klijent.print(F("ERROR, wrong command: "));
    klijent.print(device);
  }
}

// metoda koja vraca odgovarajuci thermistor objekt ovisno o pinu
TKThermistor getThermistor(int pin){
  if (pin == 0){
    TKThermistor therm(I0);
    return therm;
  }
  else if (pin == 1){
    TKThermistor therm(I1);
    return therm;
  }
  else if (pin == 2){
    TKThermistor therm(I2);
    return therm;
  }
  else if (pin == 3){
    TKThermistor therm(I3);
    return therm;
  }
  else if (pin == 4){
    TKThermistor therm(I4);
    return therm;
  }
  else{
    TKThermistor therm(I5);
    return therm;
  }
}

// metoda koja vraca odgovarajuci led objekt ovisno o pinu
TKLed getLed(int pin){
  if (pin == 0){
    TKLed led(O0);
    return led;
  }
  else if (pin == 1){
    TKLed led(O1);
    return led;
  }
  else if (pin == 2){
    TKLed led(O2);
    return led;
  }
  else if (pin == 3){
    TKLed led(O3);
    return led;
  }
  else if (pin == 4){
    TKLed led(O4);
    return led;
  }
  else{
    TKLed led(O5);
    return led;
  }
}

// metoda za obradu tinkerkit zahtjeva
void tinkerkitReq(YunClient klijent){
  
  // dohvati modul
  String module = klijent.readStringUntil('/');

  // ako se radi o thermistoru
  if (module == "thermistor"){
    // pročitaj metodu i pin
    String method = klijent.readStringUntil('/'); 
    int pin = klijent.parseInt();

    TKThermistor therm = getThermistor(pin);
    
    // obradi metodu
    if (method == "read_celsius"){
      klijent.print(therm.readCelsius());
    }
    else if (method == "read_fahrenheit"){
      klijent.print(therm.readFahrenheit());
    }
    else if (method == "read"){
      klijent.print(therm.read());
    }
    else{
      klijent.print(F("ERROR, wrong method: "));
      klijent.print(method);
    }

  }

  // ako se radi o LED-u
  else if (module == "led"){
    // pročitaj metodu i pin
    String method = klijent.readStringUntil('/'); 
    int pin = klijent.parseInt();

    TKLed led = getLed(pin);
    
    // obradi metodu i vrati klijentu odgovor (print)
    if (method == "on"){
      led.on();
      klijent.print(F("ON"));
    }
    else if (method == "off"){
      led.off();
      klijent.print(F("OFF"));
    }
    else if (method == "state"){
      klijent.print(led.state());
    }
    else if (method == "brightness"){
      int value = klijent.parseInt();
      led.brightness(value);
      klijent.print(value);
    }
    else{
      klijent.print(F("ERROR, wrong method: "));
      klijent.print(method);
    }

  }
  
  else {
    klijent.print(F("ERROR, wrong module: "));
    klijent.print(module);
  }
}

void yunReq(YunClient klijent){
  
  // dohvati modul
  String module = klijent.readStringUntil('/');

  // ako se radi o digitalnom
  if (module == "digital"){
    // pročitaj metodu i pin
    String method = klijent.readStringUntil('/'); 
    int pin = klijent.parseInt();
       
    // obradi metodu
    if (method == "read"){
      klijent.print(digitalRead(pin));
    }
    else if (method == "toggle"){
      int value = digitalRead(pin);
      if (value > 0){
        digitalWrite(pin, LOW);
        klijent.print(1);
      }
      else {
        digitalWrite(pin, HIGH);
        klijent.print(0);
      }  
      
    }
    else if (method == "write"){
      int value = klijent.parseInt();
      if (value == 0){
        digitalWrite(pin, LOW);
        klijent.print(0);
      }
      else {
        digitalWrite(pin, HIGH);
        klijent.print(1);
      }
    }
    else {
      klijent.print(F("ERROR, wrong method: "));
      klijent.print(method);
    }

  }

  // ako se radi o analogu
  else if (module == "analog"){
    // pročitaj metodu i pin
    String method = klijent.readStringUntil('/'); 
    int pin = klijent.parseInt();
        
    // obradi metodu i vrati klijentu odgovor (print)
    if (method == "read"){
      klijent.print(analogRead(pin));
    }
    else if (method == "write"){      
      int value = klijent.parseInt();
      if (value > -1 && value < 1023){
        analogWrite(pin, value);
      }
      else{
        analogWrite(pin, 1023);
      }
      klijent.print(value);
    }
    else{      
      klijent.print(F("ERROR, wrong method: "));
      klijent.print(method);
    }
  }
  else{
    klijent.print("ERROR, wrong module: ");
    klijent.print(module);
  }
}

void modeCommand(YunClient klijent) {
  // Procitaj pin
  int pin = klijent.parseInt();

  // Ako sljedeci znak nije /, vrati ERROR
  if (klijent.read() != '/') {
    klijent.print(F("ERROR, malformed URI"));
    return;
  }

  String mode = klijent.readStringUntil('\r');

  if (mode == "input") {
    pinMode(pin, INPUT);
    klijent.print(pin);
    klijent.print(F(" set as INPUT"));
    return;
  }
  else if (mode == "output") {
    pinMode(pin, OUTPUT);
    klijent.print(pin);
    klijent.print(F(" set as OUTPUT"));
    return;
  }
  else{
    klijent.print(F("ERROR, wrong mode: "));
    klijent.print(mode);
  }
}
