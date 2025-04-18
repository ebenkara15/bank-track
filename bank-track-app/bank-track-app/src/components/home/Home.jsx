import { Alert, AlertDescription, AlertIcon, AlertTitle } from "@chakra-ui/react";
import { SignInButton, SignOutButton, SignedIn, SignedOut, useUser } from "@clerk/clerk-react";

const Home = () => {
    const { user } = useUser();


    const greetings = user ? `${user.firstName} ${user.lastName} - ${user.emailAddresses[0]}` : "Guest"

    return (
        <>
            <SignedOut>
                <SignInButton />
                <p>This content is public. Only signed out users can see the SignInButton above this text.</p>
            </SignedOut>
            <SignedIn>
                <Alert status='success'>
                    <AlertIcon />
                    <AlertTitle >You are signed in!</AlertTitle>
                    <AlertDescription>Welcome back! You are signed in as {greetings}</AlertDescription>

                </Alert>
                <SignOutButton aftersignouturl="/" />
                <p>This content is private. Only signed in users can see the SignOutButton above this text.</p>
                <div>
                    <p>Signed in as: {greetings}</p>
                    {/* <Navigate to={'/accounts'} /> */}
                </div>
            </SignedIn>
        </>
    )
};

export default Home;
