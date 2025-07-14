include "poseidon2.circom";

component main = Poseidon2();

// Set inputs
main.input[0] <== 123456789;
main.input[1] <== 987654321;
main.input[2] <== 111111111;

// Output hash
log(main.output);
