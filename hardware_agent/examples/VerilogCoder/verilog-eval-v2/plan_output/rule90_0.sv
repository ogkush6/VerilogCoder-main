`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output reg load,
	output reg[511:0] data,
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
		data <= 0;
		data[0] <= 1'b1;
		load <= 1;
		@(posedge clk); wavedrom_start("Sierpi&#324;ski triangle: See Hint.");
		@(posedge clk);
		@(posedge clk);
		load <= 0;
		repeat(10) @(posedge clk);		
		wavedrom_stop();


		data <= 0;
		data[256] <= 1'b1;
		load <= 1;
		@(posedge clk);
		@(posedge clk);
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end
		data <= 512'h1000000000000001;
		load <= 1;
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end

		data <= $random;
		load <= 1;
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end

		data <= 0;
		load <= 1;
		repeat(20) @(posedge clk);
		repeat(2) @(posedge clk) data <= data + 2;
		@(posedge clk) begin 
			load <= 0;
			data <= data + 1;
		end
		repeat(20) @(posedge clk) data <= data + 1;
		repeat(500) @(posedge clk) begin
		end

		#1 $finish;
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

	logic load;
	logic [511:0] data;
	logic [511:0] q_ref;
	logic [511:0] q_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.load,
		.data );
	RefModule good1 (
		.clk,
		.load,
		.data,
		.q(q_ref) );
		
	TopModule top_module1 (
		.clk,
		.load,
		.data,
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
  input load,
  input [511:0] data,
  output reg [511:0] q
);

  always @(posedge clk) begin
    if (load)
      q <= data;
    else begin
      q <= q[$bits(q)-1:1] ^ {q[$bits(q)-2:0], 1'b0} ;
    end
  end

endmodule


module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [511:0] data,
  output logic [511:0] q
);

  // Define a 512-bit register to hold the current state of the cells
  logic [511:0] state_reg;

  // Sequential logic to load the initial state of the cells from the input data when the load signal is asserted
  always @(posedge clk) begin
    if (load)
      state_reg <= data;
    else
      state_reg <= next_state;
  end

  // Define a 512-bit wire to compute the next state of each cell based on the XOR of its two neighbors
  logic [511:0] next_state;

  // Combinational logic to compute the next state of each cell
  assign next_state[0] = state_reg[1]; // For the first cell, the left neighbor is assumed to be 0
  assign next_state[511] = state_reg[510]; // For the last cell, the right neighbor is assumed to be 0
  genvar i;
  generate
    for (i = 1; i < 511; i = i + 1) begin
      assign next_state[i] = state_reg[i-1] ^ state_reg[i+1]; // For all other cells, the next state is the XOR of the two neighbors
    end
  endgenerate

  // Assign the state of the cells to the output
  assign q = state_reg;

endmodule