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
      `https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17`,
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

    console.log('WebRTC connection successfully initialized!');
  } catch (error) {
    console.error('Error initializing WebRTC:', error);
  }
}
