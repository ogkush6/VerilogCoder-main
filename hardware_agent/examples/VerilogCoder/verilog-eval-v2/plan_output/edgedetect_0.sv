`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	input tb_match,
	output reg [7:0] in,
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
		in <= 0;
		@(posedge clk);
		wavedrom_start("");
		repeat(2) @(posedge clk);
		in <= 1;
		repeat(4) @(posedge clk);
		in <= 0;
		repeat(4) @(negedge clk);
		in <= 6;
		repeat(2) @(negedge clk);
		in <= 0;		
		repeat(2) @(posedge clk);
		wavedrom_stop();

		repeat(200)
			@(posedge clk, negedge clk) in <= $random;
		$finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_pedge;
		int errortime_pedge;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic [7:0] in;
	logic [7:0] pedge_ref;
	logic [7:0] pedge_dut;

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
		.clk,
		.in,
		.pedge(pedge_ref) );
		
	TopModule top_module1 (
		.clk,
		.in,
		.pedge(pedge_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_pedge) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "pedge", stats1.errors_pedge, stats1.errortime_pedge);
		else $display("Hint: Output '%s' has no mismatches.", "pedge");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { pedge_ref } === ( { pedge_ref } ^ { pedge_dut } ^ { pedge_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (pedge_ref !== ( pedge_ref ^ pedge_dut ^ pedge_ref ))
		begin if (stats1.errors_pedge == 0) stats1.errortime_pedge = $time;
			stats1.errors_pedge = stats1.errors_pedge+1'b1; end

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
  input [7:0] in,
  output reg [7:0] pedge
);

  reg [7:0] d_last;

  always @(posedge clk) begin
    d_last <= in;
    pedge <= in & ~d_last;
  end

endmodule


module TopModule
(
  input  logic       clk,
  input  logic [7:0] in,
  output logic [7:0] pedge
);

  // Sequential logic
  logic [7:0] prev_in;
  logic [7:0] reg_pedge; // Register for storing intermediate signal

  always @( posedge clk ) begin
    prev_in <= in;
    reg_pedge <= temp_pedge; // Update the register every clock cycle
  end

  // Combinational logic
  logic [7:0] temp_pedge;

  always @(*) begin
    temp_pedge = (in & ~prev_in);
  end

  // Structural connections
  assign pedge = reg_pedge; // Connect the output to the register

endmodule