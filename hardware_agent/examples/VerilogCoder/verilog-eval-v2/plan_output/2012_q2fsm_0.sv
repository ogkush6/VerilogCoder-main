`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic reset,
	output logic w
);

	initial begin
		repeat(200) @(negedge clk) begin
			reset <= ($random & 'h1f) == 0;
			w <= $random;
		end
		
		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_z;
		int errortime_z;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic reset;
	logic w;
	logic z_ref;
	logic z_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.reset,
		.w );
	RefModule good1 (
		.clk,
		.reset,
		.w,
		.z(z_ref) );
		
	TopModule top_module1 (
		.clk,
		.reset,
		.w,
		.z(z_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_z) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "z", stats1.errors_z, stats1.errortime_z);
		else $display("Hint: Output '%s' has no mismatches.", "z");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { z_ref } === ( { z_ref } ^ { z_dut } ^ { z_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (z_ref !== ( z_ref ^ z_dut ^ z_ref ))
		begin if (stats1.errors_z == 0) stats1.errortime_z = $time;
			stats1.errors_z = stats1.errors_z+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input clk,
  input reset,
  input w,
  output z
);

  parameter A=0,B=1,C=2,D=3,E=4,F=5;
  reg[2:0] state, next;

  always @(posedge clk)
    if (reset) state <= A;
    else state <= next;

  always_comb begin
    case (state)
      A: next = w ? B : A;
      B: next = w ? C : D;
      C: next = w ? E : D;
      D: next = w ? F : A;
      E: next = w ? E : D;
      F: next = w ? C : D;
      default: next = 'x;
    endcase
  end

  assign z = (state == E) || (state == F);

endmodule


module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic w,
  output logic z
);

  // State encoding
  localparam [2:0] STATE_A = 3'b000;
  localparam [2:0] STATE_B = 3'b001;
  localparam [2:0] STATE_C = 3'b010;
  localparam [2:0] STATE_D = 3'b011;
  localparam [2:0] STATE_E = 3'b100;
  localparam [2:0] STATE_F = 3'b101;

  // State register
  logic [2:0] state;
  logic [2:0] state_next;

  // State flip-flop logic block
  always @(posedge clk) begin
    if (reset)
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state logic block
  always @(*) begin
    state_next = state;
    case (state)
      STATE_A: state_next = w ? STATE_B : STATE_A;
      STATE_B: state_next = w ? STATE_C : STATE_D;
      STATE_C: state_next = w ? STATE_E : STATE_D;
      STATE_D: state_next = w ? STATE_F : STATE_A;
      STATE_E: state_next = w ? STATE_E : STATE_D;
      STATE_F: state_next = w ? STATE_C : STATE_D;
    endcase
  end

  // Output logic block
  always @(*) begin
    z = 1'b0;
    case (state)
      STATE_E: z = 1'b1;
      STATE_F: z = 1'b1;
      default: z = 1'b0;
    endcase
  end

endmodule