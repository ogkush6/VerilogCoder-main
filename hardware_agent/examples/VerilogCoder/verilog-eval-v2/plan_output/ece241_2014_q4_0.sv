`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic x,
	output reg[511:0] wavedrom_title,
	output reg wavedrom_enable	
);


// Add two ports to module stimulus_gen:
//    output [511:0] wavedrom_title
//    output reg wavedrom_enable

	task wavedrom_start(input[511:0] title = "");
	endtask
	
	task wavedrom_stop;
		#1;
	endtask	



	initial begin
		x <= 0;
		@(negedge clk) wavedrom_start();
			@(posedge clk) x <= 2'h0;
			@(posedge clk) x <= 2'h0;
			@(posedge clk) x <= 2'h0;
			@(posedge clk) x <= 2'h0;
			@(posedge clk) x <= 2'h1;
			@(posedge clk) x <= 2'h1;
			@(posedge clk) x <= 2'h1;
			@(posedge clk) x <= 2'h1;
		@(negedge clk) wavedrom_stop();
		repeat(100) @(posedge clk, negedge clk)
			x <= $random;

		$finish;
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

	logic x;
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
		.x );
	RefModule good1 (
		.clk,
		.x,
		.z(z_ref) );
		
	TopModule top_module1 (
		.clk,
		.x,
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
  input x,
  output z
);

  reg [2:0] s = 0;

  always @(posedge clk) begin
    s <= { s[2] ^ x, ~s[1] & x, ~s[0] | x };
  end

  assign z = ~|s;

endmodule


module TopModule
(
  input  logic clk,
  input  logic x,
  output logic z
);

  // Declare D flip-flops
  logic xor_ff, and_ff, or_ff;

  // Initialize D flip-flops to zero
  initial begin
    xor_ff = 1'b0;
    and_ff = 1'b0;
    or_ff  = 1'b0;
  end

  // XOR gate logic
  logic xor_out;
  assign xor_out = x ^ xor_ff;

  // AND gate logic
  logic and_out;
  assign and_out = x & ~and_ff;

  // OR gate logic
  logic or_out;
  assign or_out = x | ~or_ff;

  // Sequential logic for D flip-flops
  always @(posedge clk) begin
    xor_ff <= xor_out;
    and_ff <= and_out;
    or_ff  <= or_out;
  end

  // NOR gate logic
  assign z = ~(xor_ff | and_ff | or_ff);

endmodule