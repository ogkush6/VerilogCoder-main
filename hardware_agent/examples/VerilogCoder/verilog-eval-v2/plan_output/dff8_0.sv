`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output reg [7:0] d,
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


	
	always @(posedge clk, negedge clk)
		d <= $random % 256;
	
	initial begin
		@(posedge clk);
		wavedrom_start("Positive-edge triggered DFF");
		repeat(10) @(posedge clk);
		wavedrom_stop();
		#100;
		$finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_q;
		int errortime_q;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic [7:0] d;
	logic [7:0] q_ref;
	logic [7:0] q_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.d );
	RefModule good1 (
		.clk,
		.d,
		.q(q_ref) );
		
	TopModule top_module1 (
		.clk,
		.d,
		.q(q_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_q) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "q", stats1.errors_q, stats1.errortime_q);
		else $display("Hint: Output '%s' has no mismatches.", "q");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { q_ref } === ( { q_ref } ^ { q_dut } ^ { q_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (q_ref !== ( q_ref ^ q_dut ^ q_ref ))
		begin if (stats1.errors_q == 0) stats1.errortime_q = $time;
			stats1.errors_q = stats1.errors_q+1'b1; end

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
  input [7:0] d,
  output reg [7:0] q
);

  initial
    q = 8'h0;

  always @(posedge clk)
    q <= d;

endmodule


module TopModule
(
  input  logic       clk,
  input  logic [7:0] d,
  output logic [7:0] q
);

  // Initialize q to 0
  initial begin
    q <= 8'b0;
  end

  // D flip-flop for d[0] and q[0]
  always @(posedge clk) begin
    q[0] <= d[0];
  end

  // D flip-flop for d[1] and q[1]
  always @(posedge clk) begin
    q[1] <= d[1];
  end

  // D flip-flop for d[2] and q[2]
  always @(posedge clk) begin
    q[2] <= d[2];
  end

  // D flip-flop for d[3] and q[3]
  always @(posedge clk) begin
    q[3] <= d[3];
  end

  // D flip-flop for d[4] and q[4]
  always @(posedge clk) begin
    q[4] <= d[4];
  end

  // D flip-flop for d[5] and q[5]
  always @(posedge clk) begin
    q[5] <= d[5];
  end

  // D flip-flop for d[6] and q[6]
  always @(posedge clk) begin
    q[6] <= d[6];
  end

  // D flip-flop for d[7] and q[7]
  always @(posedge clk) begin
    q[7] <= d[7];
  end

endmodule