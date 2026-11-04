import "./styles.css";
export const metadata = { title: "AccessLens", description: "Web quality intelligence" };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
