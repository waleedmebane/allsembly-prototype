<?xml version="1.0" encoding="UTF-8"?>
<!--
 Copyright © 2021 Waleed H. Mebane

   This file is part of Allsembly™ Prototype.

   Allsembly™ Prototype is free software: you can redistribute it and/or
   modify it under the terms of the Lesser GNU General Public License,
   version 3, as published by the Free Software Foundation and the
   additional terms directly below this notice.

   Allsembly™ Prototype is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   Lesser GNU General Public License for more details.

   You should have received a copy of the Lesser GNU General Public
   License along with Allsembly™ Prototype.  If not, see
   <https://www.gnu.org/licenses/>.

   Additional terms:

   Without his or her specific prior written permission, neither may the names
   of any author of or contributor to this software be used to endorse products
   derived from this software nor may his or her names, image, or likeness be
   used to promote products derived from this software.

   Nothing in this license shall be interpreted as granting any license to
   any of the trademarks of any of the authors of or contributors to this
   software.
-->
<!--
This implements the client side of Allsembly, except for logging in, which
is implemented by allsembly_demo_login.xsl.
The CGI just produces a trivial XML string that contains a document root,
and a reference to this file as its default XML stylesheet.
Implementing it as an XSL template simplifies what the CGI has to do,
but will also make it easy to do localization in the future by including
(using "xsl-include") an XML file that contains the strings to use.
This approach also provides flexibility to either preload some data via XML
tags, such as to alter the page according to user preferences, or to wait
and load the data via XmlHttpRequests with Javascript.

The Javascript functions make requests to the server using JSON-RPC.
The JSON-RPC implementation is provided by the library, "simple-jsonrcp-js".

The library, "d3", is used to make the SVG image of the graph pan and
zoom in response to mouse events.

The "dialog-polfill" library provides the functionality of the <DIALOG>
tag for making modal dialogs even when the browser doesn't support it
yet.

Javascript in CGI produced responses is more difficult to debug.
If you need to, you can create an HTML version of this file.  Copy everything
from <html ...> to </html> into a separate file, named, e.g., allsembly_demo.html
and replace "&lt;" with "<" in the Javascript code.
After you have authenticated, you can point your browser at the HTML file,
and it will work just as well as this XSL file, but your browser's developer
tools can point you to the line number in the file where there is an issue and
allow you to step through the code in its debugger.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:template match="/">
<html lang="en">
<head>
<meta charset="utf-8" />
<script src="/allsembly/scripts/simple-jsonrpc-js.js"></script>
<script src="/allsembly/scripts/d3.js"></script>

<style>
* {
    box-sizing: border-box;
}
html, body {
  height: 100%;
}
	body {
		background-color: WhiteSmoke;
	}

.col-1 {
overflow: hidden;
    width: 100%;
    background-color: white;
}
/*
.col-2 {
overflow: auto;
    width: 30%;
}
*/
[class*="col-"] {
    float: left;
    padding: 15px;
    border: none;
    height: 75%;
}
.row {
overflow: auto;
    height: 100%;
/*  background-color: white;
*/
}
.row::after {
  content: "";
  clear: both;
  display: table;
}
.header {
height: 12%;
overflow: auto;
  padding: 15px;
}
.footer {
overflow: auto;
  padding: 15px;
}
</style>
</head>
<body>
	<div class="header">
		<table style="border: none">
			<tr>
				<td>
					<form id="add_initial_position_form">
						<button type="submit" id="initial_position_button" value="Add initial position">Add Initial Position</button>
					</form>
				</td>
				<td>
					<form id="clear_graph_form">
						<button type="submit" id="clear_graph_button" value="Clear graph">Clear Graph</button>
					</form>
				</td>
			</tr>
		</table>
	</div>
    <div class="row">
		<div id='svg' class="col-1">
		</div>
    </div>
	<div class="footer">
		<form>
			<button disabled="disabled">Search</button>
			<input style="width: 80%" value="Not implemented, yet."/>
		</form>
	</div>
	<dialog style="width:500px" id ="positAddDialog" >
		<!-- Modal dialog box for adding an initial position -->
		<form method="dialog">
		   <p>
		  <label>Initial position text:</label><br />
		  <textarea id="position_text"></textarea>
		  </p>
		  <button value="OK">OK</button>
		  <button value="Cancel">Cancel</button>
		</form>
	</dialog>
	<dialog style="width:500px" id ="positShowDialog" >
		<!-- Modal dialog box for showing a positions full text
		     and showing position options, such as to create
		     a new argument pro or con the position, "Argue".
		-->
		<form method="dialog">
			<input id="position_id" type="hidden" />
			<div id="posit_details_div"></div>
			<button value="Argue">Argue</button>
			<!-- Disabled buttons are to show future features to expect -->
			<button disabled="true" value="Relate">Relate</button>
			<button disabled="true" value="Discuss">Discuss</button>
			<button disabled="true" value="Bet">Bet</button>

			<button value="Cancel">Cancel</button>
		</form>
	</dialog>
	<dialog style="width:500px" id ="argueDialog" >
		<!-- Modal dialog bod for adding a new argument -->
		<form id="argueDialogForm" method="dialog">
			<input type="hidden" id="target_position_text" />
			<input id="target_position" type="hidden" />
			<p>
			<label>Argument type:</label><br />
				<label>Pro</label>
			<input type="radio" name="pro_or_con" value="support" checked="true" /><br />
				<label>Con</label>
			<input type="radio" name="pro_or_con" value="oppose" />
			</p>
			<p>
			<label>Premises:</label><br />
			<textarea id="first_premise" ></textarea>
			<label>Bid: </label><input id="bid_on_first_premise" value="51.0" />
			<br /> <button disabled="true">Add premise</button>
			</p>
			<p>
			<label>Inferential premise (optional):</label><br />
			<textarea id="inf_premise" ></textarea>
			<label>Bid: </label><input id="bid_on_inf_premise" value="99.9" />
			</p>
			<button value="OK">OK</button>
			<button value="Cancel">Cancel</button>
		</form>
	</dialog>

	<script src="/allsembly/scripts/dialog-polyfill.js"></script>
	<script>
		var positAddDialog = document.getElementById('positAddDialog');
		positAddDialog.addEventListener('close', positDialogOnClose);
		dialogPolyfill.registerDialog(positAddDialog);
		function showPositAddDialog(event) {
			//function to open the dialog for adding an initial position
			positAddDialog.showModal();
			event.preventDefault();
			return false;
		}
		var initialPositionForm = document.getElementById('add_initial_position_form');
		initialPositionForm.addEventListener('submit', showPositAddDialog);
		var clearGraphForm = document.getElementById('clear_graph_form');
		clearGraphForm.addEventListener('submit', clearGraph);
		var positShowDialog = document.getElementById('positShowDialog');
		positShowDialog.addEventListener('close', positShowOnClose);
		dialogPolyfill.registerDialog(positShowDialog);
		var argueDialog = document.getElementById('argueDialog');
		argueDialog.addEventListener('close', argueOnClose);
		dialogPolyfill.registerDialog(argueDialog);

		var d = new Date();
		var t = d.getTime();
		var jrpc = simple_jsonrpc.connect_xhr('allsembly_demo.py');

		function zoomed({transform}) {
			//callback function, used by the d3 library to implement
			//panning and zooming in the SVG image (the argument graph)
			//pan with click and drag and zoom with the mouse scroll wheel.
		   	document.querySelector("#svg svg").setAttribute("transform", transform);
		}

		function get_arg_graph() {
			//load the argument graph SVG string and overwrite the previous graph
			jrpc.call('get_arg_graph', [0]).then(function(res) {
				console.log(res);
				var elem = document.querySelector('#svg');
				elem.innerHTML = res;
				if (res != "") {
					var svgn = document.querySelector("#svg svg").getAttribute("transform");
					var trf = document.querySelector("#svg svg g").getAttribute("transform");
					console.log(trf);
					if (-1 != trf.indexOf("translate")) {
						var trf_split = trf.split("translate(");
						var trans = trf_split[1].split(" ");
						var trans_x = parseFloat(trans[0]);
						var trans_y = parseFloat(trans[1]);
					}
					console.log(trans_x);
					console.log(trans_y);
					var d3trans = d3.zoomTransform(trf);
					console.log(d3trans);

					var selection = d3.select("svg g");
					zoom = d3.zoom().on("zoom", zoomed);

					zoom(selection);
					d3.select("svg").style("background-color", "white");
					d3.select("svg").style("display", "inline-block");
				}
			});
		}

		//load the initial argument graph on startup
		get_arg_graph();

		function positDialogOnClose() {
			if (positAddDialog.returnValue == "OK")
				add_node(document.getElementById("position_text").value);
			return false;
		}

		function positShowOnClose() {
			if (positShowDialog.returnValue == "Argue") {
				document.getElementById("target_position").value =
				  document.getElementById("position_id").value;
				document.getElementById("target_position_text").value =
				  document.getElementById("position_text").value;
				argueDialog.showModal();//open argue dialog
			}
			return false;
		}

		function argueOnClose() {
			if (argueDialog.returnValue == "OK") {
				first_premise = document.getElementById("first_premise").value
				bid_on_first_premise = parseFloat(document.getElementById("bid_on_first_premise").value)
				inf_premise = document.getElementById("inf_premise").value
				bid_on_inf_premise = parseFloat(document.getElementById("bid_on_inf_premise").value)
				argument_is_PRO = document.getElementsByName("pro_or_con")[0].checked

				//validate the inputs
				if ("" == first_premise) {
					alert("'Premises' is a required field.")
				}
				else if ( !Number.isFinite(bid_on_first_premise) ||
							bid_on_first_premise &lt;= 0.0 ||
							bid_on_first_premise >= 100.0 ||
						  !Number.isFinite(bid_on_inf_premise) ||
							bid_on_inf_premise &lt;= 0.0 ||
							bid_on_inf_premise >= 100.0) {
					alert("Bid must be a number between 0 and 100, exclusive.")
				}
				else {
					if ("" == inf_premise) {
						inf_premise = "IF " + first_premise
									  + "\nTHEN "
		                              + (argument_is_PRO ? "" : "NOT ")
		                              + document.getElementById("posit_details_div").innerHTML
									  ;
					}
					//make the request to the server to add the argument
					add_argument(document.getElementsByName("pro_or_con")[0].checked,
								 document.getElementById("target_position").value,
								 document.getElementById("first_premise").value,
								 document.getElementById("bid_on_first_premise").value,
								 inf_premise,
								 document.getElementById("bid_on_inf_premise").value
								);
				}
			}
			return false;
		}

		function add_node(a) {
			var d = new Date();
			var t = d.getTime();
			jrpc.call('propose', [0, "", a]).then(function(res) {
				console.log(res);
				get_arg_graph();
			});
			return true;
		}

		  function clearGraph() {
			if (confirm("Are you sure you want to clear the graph, deleting all nodes?")) {
				jrpc.call('clear_graph').then(function(res) {
					console.log(res);
					get_arg_graph();
				});
			}
			event.preventDefault();
			return false;
		}

		function show_position_details(pos_id) {
			jrpc.call('get_position_details', [0, pos_id]).then(function(res) {
				console.log(res);
				document.getElementById("posit_details_div").innerHTML = res;
				document.getElementById("position_id").value = pos_id;
				positShowDialog.showModal();
			});
			return true;
		}

		function add_argument(arg_is_support_arg,
							  target_position,
							  first_premise,
							  bid_on_first_premise,
							  inf_premise,
							  bid_on_inf_premise) {
			jrpc.call('argue', [0, /*issue*/
								"", /*subuser*/
								arg_is_support_arg,
								parseInt(target_position),
								null, /*bid on target*/
								1,
								first_premise,
								parseFloat(bid_on_first_premise),
								1, /*bid amount on first premise */
								inf_premise,
								parseFloat(bid_on_inf_premise),
								1 /*bid amount on inf premise */
							   ]).then(function(res) {
				get_arg_graph();
			});
			return true;
		}
	</script>
</body>
</html>
	</xsl:template>
</xsl:stylesheet>