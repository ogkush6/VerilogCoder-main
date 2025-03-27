`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	input tb_match,
	output logic [3:0] in,
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
		in <= 4'h3;
		@(negedge clk);
		wavedrom_start();
			@(posedge clk) in <= 3;
			@(posedge clk) in <= 6;
			@(posedge clk) in <= 12;
			@(posedge clk) in <= 9;
			@(posedge clk) in <= 5;
		@(negedge clk);
		wavedrom_stop();
		in <= $random;
		repeat(100) begin
			@(negedge clk) in <= $random;
			@(posedge clk) in <= $random;
		end
		#1 $finish;
	end
		
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_out_both;
		int errortime_out_both;
		int errors_out_any;
		int errortime_out_any;
		int errors_out_different;
		int errortime_out_different;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic [3:0] in;
	logic [3:0] out_both_ref;
	logic [3:0] out_both_dut;
	logic [3:0] out_any_ref;
	logic [3:0] out_any_dut;
	logic [3:0] out_different_ref;
	logic [3:0] out_different_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.in );
	RefModule good1 (
		.in,
		.out_both(out_both_ref),
		.out_any(out_any_ref),
		.out_different(out_different_ref) );
		
	TopModule top_module1 (
		.in,
		.out_both(out_both_dut),
		.out_any(out_any_dut),
		.out_different(out_different_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_out_both) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out_both", stats1.errors_out_both, stats1.errortime_out_both);
		else $display("Hint: Output '%s' has no mismatches.", "out_both");
		if (stats1.errors_out_any) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out_any", stats1.errors_out_any, stats1.errortime_out_any);
		else $display("Hint: Output '%s' has no mismatches.", "out_any");
		if (stats1.errors_out_different) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out_different", stats1.errors_out_different, stats1.errortime_out_different);
		else $display("Hint: Output '%s' has no mismatches.", "out_different");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { out_both_ref, out_any_ref, out_different_ref } === ( { out_both_ref, out_any_ref, out_different_ref } ^ { out_both_dut, out_any_dut, out_different_dut } ^ { out_both_ref, out_any_ref, out_different_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (out_both_ref !== ( out_both_ref ^ out_both_dut ^ out_both_ref ))
		begin if (stats1.errors_out_both == 0) stats1.errortime_out_both = $time;
			stats1.errors_out_both = stats1.errors_out_both+1'b1; end
		if (out_any_ref !== ( out_any_ref ^ out_any_dut ^ out_any_ref ))
		begin if (stats1.errors_out_any == 0) stats1.errortime_out_any = $time;
			stats1.errors_out_any = stats1.errors_out_any+1'b1; end
		if (out_different_ref !== ( out_different_ref ^ out_different_dut ^ out_different_ref ))
		begin if (stats1.errors_out_different == 0) stats1.errortime_out_different = $time;
			stats1.errors_out_different = stats1.errors_out_different+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input  [3:0] in,
  output [3:0] out_both,
  output [3:0] out_any,
  output [3:0] out_different
);

  assign out_both[2:0] = in[2:0] & in[3:1];
  assign out_any[3:1]  = in[2:0] | in[3:1];
  assign out_different = in^{in[0], in[3:1]};

  // we don't care about out_both[3] or out_any[0]
  assign out_both[3] = 1'bx;
  assign out_any[0]  = 1'bx;

endmodule


module TopModule
(
  input  logic [3:0] in,
  output logic [3:0] out_both,
  output logic [3:0] out_any,
  output logic [3:0] out_different
);

  // Combinational logic for out_both[0]
  assign out_both[0] = in[0] & in[1];

  // Combinational logic for out_both[1]
  assign out_both[1] = in[1] & in[2];

  // Combinational logic for out_both[2]
  assign out_both[2] = in[2] & in[3];

  // Combinational logic for out_any[1]
  assign out_any[1] = in[1] | in[0];

  // Combinational logic for out_any[2]
  assign out_any[2] = in[2] | in[1];

  // Combinational logic for out_any[3]
  assign out_any[3] = in[3] | in[2];

  // Combinational logic for out_different[0]
  assign out_different[0] = in[0] ^ in[1];

  // Combinational logic for out_different[1]
  assign out_different[1] = in[1] ^ in[2];

  // Combinational logic for out_different[2]
  assign out_different[2] = in[2] ^ in[3];

  // Combinational logic for out_different[3]
  assign out_different[3] = in[3] ^ in[0];

endmodule