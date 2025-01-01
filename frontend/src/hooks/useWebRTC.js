export async function initializeWebRTC() {
  try {
    // Create a new WebRTC PeerConnection
    const pc = new RTCPeerConnection();

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
      console.log('Received remote track:', event.streams[0]);
      const audio = new Audio();
      audio.srcObject = event.streams[0];
      audio.autoplay = true; // Automatically play the audio
    };

    // Create an SDP offer and set it as the local description
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send the SDP offer to OpenAI's server
    const sdpResponse = await fetch(
      `https://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${client_secret}`,
          'Content-Type': 'application/sdp',
        },
        body: offer.sdp,
      }
    );

    if (!sdpResponse.ok) {
      throw new Error(`Failed to exchange SDP: ${sdpResponse.statusText}`);
    }

    // Set the server's SDP answer as the remote description
    const answer = { type: 'answer', sdp: await sdpResponse.text() };
    await pc.setRemoteDescription(answer);

    // Debugging ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('New ICE Candidate:', event.candidate);
      } else {
        console.log('All ICE candidates have been sent.');
      }
    };

    // Create a DataChannel for tool communication
    const dataChannel = pc.createDataChannel("oai-tools");

    // Tool functions
    const fns = {
      queryPinecone: async ({ query }) => {
        try {
          const response = await fetch("http://localhost:5000/query-pinecone", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
          });

          if (!response.ok) {
            throw new Error(`Error querying Pinecone: ${response.statusText}`);
          }

          const data = await response.json();
          if (data.success) {
            return { success: true, results: data.results };
          } else {
            return { success: false, error: data.error };
          }
        } catch (error) {
          console.error("Error calling Pinecone query endpoint:", error);
          return { success: false, error: error.message };
        }
      },
    };

    // Advertise tools to OpenAI
    function configureData() {
      const event = {
        type: 'session.update',
        session: {
          modalities: ['text'],
          tools: [
            {
              type: 'function',
              name: 'queryPinecone',
              description: 'Use it when user asks anything about pipes, Amiblu products or anything related to current projects. This has to be always use to ensure that You are using proper and true data',
              parameters: {
                type: 'object',
                properties: {
                  query: { type: 'string', description: 'The text query to search for to answer user question. Be precise and descriptive' },
                },
              },
            },
          ],
        },
      };
      dataChannel.send(JSON.stringify(event));
    }

    dataChannel.addEventListener('open', (ev) => {
      console.log('DataChannel opened:', ev);
      configureData();
    });

    // Handle messages from OpenAI
    dataChannel.addEventListener('message', async (ev) => {
      const msg = JSON.parse(ev.data);

      if (msg.type === 'response.function_call_arguments.done') {
        const fn = fns[msg.name];
        if (fn) {
          console.log(`Calling local function ${msg.name} with ${msg.arguments}`);
          const args = JSON.parse(msg.arguments);
          const result = await fn(args);

          const event = {
            type: 'conversation.item.create',
            item: {
              type: 'function_call_output',
              call_id: msg.call_id,
              output: JSON.stringify(result),
            },
          };
          dataChannel.send(JSON.stringify(event));
        }
      }
    });

    console.log('WebRTC connection successfully initialized!');
  } catch (error) {
    console.error('Error initializing WebRTC:', error);
  }
}
