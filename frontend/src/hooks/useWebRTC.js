export async function initializeWebRTC() {
  try {
    // 1. Create a new WebRTC PeerConnection
    const pc = new RTCPeerConnection();

    // ------------------- ADDED CODE: Data channel creation -------------------
    // Create a data channel so we can exchange JSON events with the LLM
    const dataChannel = pc.createDataChannel("oai-events");
    
    // This function implements the local "search" tool:
    async function handleSearch({ query, top_k = 5 }) {
      try {
        const response = await fetch('http://localhost:5000/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query,
            top_k
          })
        });

        if (!response.ok) {
          return {
            error: true,
            message: `Search failed: ${response.statusText}. Please try asking your question differently.`,
            status: response.status
          };
        }

        const data = await response.json();
        console.log("Search results:", data);
        
        if (!data.results || data.results.length === 0) {
          return {
            error: true,
            message: "No results found. Please try a different search query.",
            results: []
          };
        }

        return data;
      } catch (error) {
        console.error("Error in search function:", error);
        return {
          error: true,
          message: "An error occurred while searching. Please try again.",
          details: error.message
        };
      }
    }

    // We'll configure the data channel once it's open
    dataChannel.addEventListener("open", () => {
      console.log("Data channel is open, sending session config with tools...");

      // 2. Send a session.update message with the new "search" tool definition
      const event = {
        type: "session.update",
        session: {
          modalities: ["text", "audio"],  // example modalities
          tools: [
            // The "search" function definition
            {
              type: "function",
              name: "search",
              description: "Search through the vector database using semantic search",
              parameters: {
                type: "object",
                properties: {
                  query: {
                    type: "string",
                    description: "The search query text"
                  },
                  top_k: {
                    type: "number",
                    description: "Number of results to return",
                    default: 5
                  }
                },
                required: ["query"]
              }
            }
          ]
        }
      };
      dataChannel.send(JSON.stringify(event));
    });

    // 3. Listen for function calls from the LLM
    dataChannel.addEventListener("message", async (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        
        // We check if the LLM is calling a function:
        // (e.g. "response.function_call_arguments.done")
        if (msg.type === "response.function_call_arguments.done") {
          const functionName = msg.name;
          const args = JSON.parse(msg.arguments);

          console.log(`Received function call for: ${functionName}`, args);

          let result = null;

          // 4. Implement your local function call
          if (functionName === "search") {
            // Call our local handleSearch
            result = await handleSearch(args);
          }

          if (result !== null) {
            // Send the function call output back to the LLM
            const returnEvent = {
              type: "conversation.item.create",
              item: {
                type: "function_call_output",
                call_id: msg.call_id,
                output: JSON.stringify(result)
              }
            };
            dataChannel.send(JSON.stringify(returnEvent));
          }
        }
      } catch (err) {
        console.error("Error parsing message from LLM:", err);
      }
    });
    // ------------------- END OF ADDED CODE -----------------------------------


    // Fetch an ephemeral key from your backend
    const response = await fetch("http://localhost:5000/session");
    if (!response.ok) {
      throw new Error(`Failed to fetch session: ${response.statusText}`);
    }

    // Extract the client_secret
    const responseJson = await response.json();
    const client_secret = responseJson.client_secret.value;
    console.log("Extracted Client Secret:", client_secret);

    // Access the microphone and add audio tracks to the PeerConnection
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    // Handle incoming audio from the OpenAI server
    pc.ontrack = (event) => {
      console.log("Received remote track:", event.streams[0]);
      const audio = new Audio();
      audio.srcObject = event.streams[0];
      audio.autoplay = true; // Automatically play the audio
    };

    // Create an SDP offer and set it as the local description
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send the SDP offer to OpenAI's server
    const sdpResponse = await fetch(
      "https://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${client_secret}`,
          "Content-Type": "application/sdp"
        },
        body: offer.sdp
      }
    );

    if (!sdpResponse.ok) {
      throw new Error(`Failed to exchange SDP: ${sdpResponse.statusText}`);
    }

    // Set the server's SDP answer as the remote description
    const answer = { type: "answer", sdp: await sdpResponse.text() };
    await pc.setRemoteDescription(answer);

    // Debugging ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        console.log("New ICE Candidate:", event.candidate);
      } else {
        console.log("All ICE candidates have been sent.");
      }
    };

    console.log("WebRTC connection successfully initialized!");
  } catch (error) {
    console.error("Error initializing WebRTC:", error);
  }
}
