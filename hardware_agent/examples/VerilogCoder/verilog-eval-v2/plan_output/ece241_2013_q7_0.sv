`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic j, k,
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
		{j,k} <= 1;
		
		@(negedge clk) wavedrom_start();
			@(posedge clk) {j,k} <= 2'h1;
			@(posedge clk) {j,k} <= 2'h2;
			@(posedge clk) {j,k} <= 2'h3;
			@(posedge clk) {j,k} <= 2'h3;
			@(posedge clk) {j,k} <= 2'h3;
			@(posedge clk) {j,k} <= 2'h0;
			@(posedge clk) {j,k} <= 2'h0;
			@(posedge clk) {j,k} <= 2'h0;
			@(posedge clk) {j,k} <= 2'h2;
			@(posedge clk) {j,k} <= 2'h2;
		@(negedge clk) wavedrom_stop();
		repeat(400) @(posedge clk, negedge clk)
			{j,k} <= $random;
		$finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_Q;
		int errortime_Q;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic j;
	logic k;
	logic Q_ref;
	logic Q_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.j,
		.k );
	RefModule good1 (
		.clk,
		.j,
		.k,
		.Q(Q_ref) );
		
	TopModule top_module1 (
		.clk,
		.j,
		.k,
		.Q(Q_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_Q) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "Q", stats1.errors_Q, stats1.errortime_Q);
		else $display("Hint: Output '%s' has no mismatches.", "Q");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { Q_ref } === ( { Q_ref } ^ { Q_dut } ^ { Q_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (Q_ref !== ( Q_ref ^ Q_dut ^ Q_ref ))
		begin if (stats1.errors_Q == 0) stats1.errortime_Q = $time;
			stats1.errors_Q = stats1.errors_Q+1'b1; end

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
  input j,
  input k,
  output reg Q
);

  always @(posedge clk)
    Q <= j&~Q | ~k&Q;

endmodule


module TopModule
(
  input  logic clk,
  input  logic j,
  input  logic k,
  output logic Q
);

  // Register to hold the current state of the output Q
  logic Q_reg;

  // Sequential logic
  always @(posedge clk) begin
    if (j == 0 && k == 0)
      Q_reg <= Q_reg; // Q = Qold
    else if (j == 0 && k == 1)
      Q_reg <= 0; // Q = 0
    else if (j == 1 && k == 0)
      Q_reg <= 1; // Q = 1
    else if (j == 1 && k == 1)
      Q_reg <= ~Q_reg; // Q = ~Qold
  end

  // Structural connections
  assign Q = Q_reg;

endmodule